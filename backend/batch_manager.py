# backend/batch_manager.py
"""
Batch Management & Historical Persistence Module:
- Manages discrete import batches (weekly, monthly, or on-demand)
- Saves and archives raw files per batch
- Allows appending/importing additional files into existing batches
- In-place manual editing of doctor attendance records with auto-recalculation
- Pre-generates and updates PDF and Excel reports per batch
"""

import os
import json
import shutil
import glob
from datetime import datetime
from typing import List, Dict, Any, Optional, Union

from .data_loader import load_employee_master, load_auth_logs, get_dynamic_filter_options
from .shift_engine import process_all_doctors, minutes_to_hh_mm, classify_shift, calculate_deficit_and_overtime
from .excel_generator import generate_excel_report
from .pdf_generator import generate_pdf_report
from .config import SECTOR_LOCATIONS_MAP, DEVICE_NAME_TO_INFO, is_doctor_title

STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage", "batches"))
INDEX_FILE = os.path.join(STORAGE_DIR, "batches_index.json")

os.makedirs(STORAGE_DIR, exist_ok=True)


def load_batches_index() -> List[Dict[str, Any]]:
    """Loads the index of all saved batches."""
    if not os.path.exists(INDEX_FILE):
        return []
    try:
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[BatchManager] Error reading index: {e}")
        return []


def save_batches_index(batches: List[Dict[str, Any]]):
    """Saves the batches index to disk."""
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(batches, f, ensure_ascii=False, indent=2)


def get_default_docs_files():
    """Returns the default master and auth files from the docs/ directory."""
    docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs"))
    default_masters = glob.glob(os.path.join(docs_dir, "*بيانات الموظفين*.xlsx"))
    default_auths = sorted(glob.glob(os.path.join(docs_dir, "AuthLogList*.xlsx")))
    return {
        "master": default_masters[0] if default_masters else None,
        "auths": default_auths
    }


def create_batch(
    batch_name: Optional[str] = None,
    master_file_source_paths: Optional[Union[str, List[str]]] = None,
    auth_file_source_paths: Optional[List[str]] = None,
    notes: Optional[str] = None,
    master_file_source_path: Optional[str] = None # backward compatibility alias
) -> Dict[str, Any]:
    """
    Creates a new batch, copies raw files into storage, processes attendance, and persists everything.
    Supports multiple master files and multiple auth log files.
    If master files or auth files are null/empty, defaults from docs/ are used automatically.
    """
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_id = f"batch_{timestamp_str}"
    batch_dir = os.path.join(STORAGE_DIR, batch_id)
    raw_dir = os.path.join(batch_dir, "raw")
    output_dir = os.path.join(batch_dir, "output")

    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # Normalize master paths
    m_paths = []
    if master_file_source_paths:
        if isinstance(master_file_source_paths, str):
            m_paths = [master_file_source_paths]
        else:
            m_paths = list(master_file_source_paths)
    elif master_file_source_path:
        m_paths = [master_file_source_path]

    # Resolve defaults if null or empty
    defaults = get_default_docs_files()
    if not m_paths:
        if defaults["master"]:
            m_paths = [defaults["master"]]

    if not auth_file_source_paths:
        auth_file_source_paths = defaults["auths"]
        if not auth_file_source_paths:
            raise FileNotFoundError("ملفات سجلات البصمة غير محددة ولم يتم العثور على ملفات افتراضية في docs/")

    # 1. Copy Master Files into raw_dir
    master_dest_paths = []
    master_dest_names = []
    for mp in m_paths:
        if mp and os.path.exists(mp):
            m_name = os.path.basename(mp)
            m_dest = os.path.join(raw_dir, m_name)
            shutil.copy2(mp, m_dest)
            master_dest_paths.append(m_dest)
            master_dest_names.append(m_name)

    # 2. Copy AuthLog Files into raw_dir
    auth_dest_paths = []
    auth_dest_names = []
    for af in auth_file_source_paths:
        if af and os.path.exists(af):
            af_name = os.path.basename(af)
            af_dest = os.path.join(raw_dir, af_name)
            shutil.copy2(af, af_dest)
            auth_dest_paths.append(af_dest)
            auth_dest_names.append(af_name)

    # 3. Load & Process with fault tolerance
    df_master = load_employee_master(master_dest_paths)
    df_auth = load_auth_logs(auth_dest_paths)

    filter_options = get_dynamic_filter_options(df_master, df_auth)
    processed = process_all_doctors(df_master, df_auth, only_with_punches=True)

    # 4. Save processed json and filter options for instant retrieval
    processed_json_path = os.path.join(batch_dir, "processed_data.json")
    with open(processed_json_path, "w", encoding="utf-8") as f:
        json.dump(processed, f, ensure_ascii=False)

    filter_options_path = os.path.join(batch_dir, "filter_options.json")
    with open(filter_options_path, "w", encoding="utf-8") as f:
        json.dump(filter_options, f, ensure_ascii=False)

    # 5. Pre-generate excel export file (instant, ~1s)
    excel_path = os.path.join(output_dir, "Attendance_Report.xlsx")
    generate_excel_report(processed, excel_path)
    # PDF is generated on-demand via /api/export/pdf to ensure sub-3-second batch creation

    date_range_str = ""
    if filter_options.get("date_min") and filter_options.get("date_max"):
        date_range_str = f"{filter_options['date_min']} إلى {filter_options['date_max']}"

    # 6. Build Batch Metadata
    batch_meta = {
        "id": batch_id,
        "name": batch_name.strip() if batch_name else f"دفعة استيراد {timestamp_str}",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "notes": notes or "",
        "date_range": date_range_str,
        "date_min": filter_options.get("date_min"),
        "files_count": len(master_dest_names) + len(auth_dest_names),
        "master_files": master_dest_names,
        "master_file": master_dest_names[0] if master_dest_names else "docs/default",
        "auth_files": auth_dest_names,
        "summary": processed["summary"],
        "doctors_count": len(processed["doctors"]),
        "is_edited": False,
        "last_edited_at": None,
        "batch_dir": batch_dir
    }

    # 7. Update Index
    index = load_batches_index()
    index.insert(0, batch_meta)
    save_batches_index(index)

    return batch_meta


def append_files_to_batch(
    batch_id: str,
    new_auth_file_paths: List[str],
    new_master_file_path: Optional[str] = None,
    new_master_file_paths: Optional[Union[List[str], str]] = None
) -> Dict[str, Any]:
    """
    Appends new auth log files (and optionally an updated master file) to an existing batch,
    and re-runs the consolidation and export generation.
    """
    batch_dir = os.path.join(STORAGE_DIR, batch_id)
    if not os.path.exists(batch_dir):
        raise FileNotFoundError(f"Batch {batch_id} not found.")

    raw_dir = os.path.join(batch_dir, "raw")
    output_dir = os.path.join(batch_dir, "output")

    # 1. Update Master file(s) if provided
    m_incoming = []
    if new_master_file_paths:
        if isinstance(new_master_file_paths, str):
            m_incoming.append(new_master_file_paths)
        else:
            m_incoming.extend(new_master_file_paths)
    if new_master_file_path:
        m_incoming.append(new_master_file_path)

    for mp in m_incoming:
        if mp and os.path.exists(mp):
            m_name = os.path.basename(mp)
            m_dest = os.path.join(raw_dir, m_name)
            shutil.copy2(mp, m_dest)

    # 2. Add new Auth files
    for af in (new_auth_file_paths or []):
        if af and os.path.exists(af):
            af_name = os.path.basename(af)
            af_dest = os.path.join(raw_dir, af_name)
            shutil.copy2(af, af_dest)

    # 3. Reload all files currently in raw_dir
    raw_files = [os.path.join(raw_dir, f) for f in os.listdir(raw_dir) if f.endswith(('.xlsx', '.xls'))]
    emp_candidates = [f for f in raw_files if "AuthLog" not in os.path.basename(f)]
    auth_candidates = [f for f in raw_files if "AuthLog" in os.path.basename(f) or "بيانات" not in os.path.basename(f)]

    df_master = load_employee_master(emp_candidates if emp_candidates else None)
    df_auth = load_auth_logs(auth_candidates if auth_candidates else None)

    filter_options = get_dynamic_filter_options(df_master, df_auth)
    processed = process_all_doctors(df_master, df_auth, only_with_punches=True)

    # 4. Save updated processed data and cache filter options
    processed_json_path = os.path.join(batch_dir, "processed_data.json")
    with open(processed_json_path, "w", encoding="utf-8") as f:
        json.dump(processed, f, ensure_ascii=False)

    filter_options_path = os.path.join(batch_dir, "filter_options.json")
    with open(filter_options_path, "w", encoding="utf-8") as f:
        json.dump(filter_options, f, ensure_ascii=False)

    # 5. Re-generate Excel export file (instant) & clear stale PDF cache
    excel_path = os.path.join(output_dir, "Attendance_Report.xlsx")
    generate_excel_report(processed, excel_path)

    pdf_path = os.path.join(output_dir, "Attendance_Report.pdf")
    if os.path.exists(pdf_path):
        try:
            os.remove(pdf_path)
        except Exception:
            pass

    date_range_str = ""
    if filter_options.get("date_min") and filter_options.get("date_max"):
        date_range_str = f"{filter_options['date_min']} إلى {filter_options['date_max']}"

    # 6. Update Batch Metadata in Index
    index = load_batches_index()
    m_dest_names = [os.path.basename(f) for f in emp_candidates]
    a_dest_names = [os.path.basename(f) for f in auth_candidates]
    for b in index:
        if b["id"] == batch_id:
            b["files_count"] = len(raw_files)
            b["master_files"] = m_dest_names
            b["master_file"] = m_dest_names[0] if m_dest_names else "docs/default"
            b["auth_files"] = a_dest_names
            b["date_range"] = date_range_str
            b["date_min"] = filter_options.get("date_min")
            b["date_max"] = filter_options.get("date_max")
            b["doctors_count"] = len(processed["doctors"])
            b["summary"] = processed["summary"]
            b["last_updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            break
    save_batches_index(index)

    return next(b for b in index if b["id"] == batch_id)


def update_doctor_records(
    batch_id: str,
    emp_code: str,
    updated_records: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Saves user manual edits to a doctor's attendance records, recalculates doctor and batch totals,
    and updates the persisted JSON, Excel, and PDF files.
    """
    batch_dir = os.path.join(STORAGE_DIR, batch_id)
    json_path = os.path.join(batch_dir, "processed_data.json")
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Batch data not found for {batch_id}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    doctor = next((d for d in data.get("doctors", []) if d["emp_code"] == str(emp_code).strip()), None)
    if not doctor:
        raise ValueError(f"Doctor {emp_code} not found in batch {batch_id}")

    # Helper function to parse "H:MM" to minutes
    def parse_time_str_to_mins(t_str: str) -> int:
        if not t_str or ":" not in str(t_str):
            return 0
        try:
            parts = str(t_str).strip().split(":")
            return int(parts[0]) * 60 + int(parts[1])
        except Exception:
            return 0

    # Clean and recalculate each record's minutes
    for r in updated_records:
        # Check time spent minutes
        if "time_spent_minutes" not in r or not r["time_spent_minutes"]:
            r["time_spent_minutes"] = parse_time_str_to_mins(r.get("time_spent", "0:00"))

        if "deficit_minutes" not in r or not r["deficit_minutes"]:
            r["deficit_minutes"] = parse_time_str_to_mins(r.get("deficit_time", "0:00"))

        if "overtime_minutes" not in r or not r["overtime_minutes"]:
            r["overtime_minutes"] = parse_time_str_to_mins(r.get("overtime_time", "0:00"))

        r["is_deficit"] = r["deficit_minutes"] > 0
        r["is_overtime"] = r["overtime_minutes"] > 0

    doctor["records"] = updated_records

    # Recalculate Doctor Totals
    doc_hours = sum(r["time_spent_minutes"] for r in updated_records)
    doc_deficit = sum(r["deficit_minutes"] for r in updated_records)
    doc_overtime = sum(r["overtime_minutes"] for r in updated_records)

    doctor["total_days_worked"] = len([r for r in updated_records if r["time_spent_minutes"] > 0])
    doctor["total_time_spent"] = minutes_to_hh_mm(doc_hours)
    doctor["total_time_spent_minutes"] = doc_hours
    doctor["total_deficit"] = minutes_to_hh_mm(doc_deficit)
    doctor["total_deficit_minutes"] = doc_deficit
    doctor["total_overtime"] = minutes_to_hh_mm(doc_overtime)
    doctor["total_overtime_minutes"] = doc_overtime

    # Recalculate Batch Totals
    all_hours = sum(d["total_time_spent_minutes"] for d in data["doctors"])
    all_deficit = sum(d["total_deficit_minutes"] for d in data["doctors"])
    all_overtime = sum(d["total_overtime_minutes"] for d in data["doctors"])

    data["summary"] = {
        "total_doctors": len(data["doctors"]),
        "total_hours": minutes_to_hh_mm(all_hours),
        "total_deficit": minutes_to_hh_mm(all_deficit),
        "total_overtime": minutes_to_hh_mm(all_overtime)
    }

    # Save updated processed_data.json
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

    # Re-generate batch output files
    output_dir = os.path.join(batch_dir, "output")
    excel_path = os.path.join(output_dir, "Attendance_Report.xlsx")
    generate_excel_report(data, excel_path)

    pdf_path = os.path.join(output_dir, "Attendance_Report.pdf")
    generate_pdf_report(data, pdf_path)

    # Update metadata index
    index = load_batches_index()
    for b in index:
        if b["id"] == batch_id:
            b["summary"] = data["summary"]
            b["is_edited"] = True
            b["last_edited_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            break
    save_batches_index(index)

    return {
        "success": True,
        "doctor": doctor,
        "batch_summary": data["summary"]
    }


def enrich_batch_processed_data(data: Dict[str, Any], batch_dir: str) -> Dict[str, Any]:
    """Auto-enriches batch processed data with sector, is_doctor, terminals and device mappings."""
    if not data or "doctors" not in data or not data["doctors"]:
        return data

    first_doc = data["doctors"][0]
    if first_doc.get("sector") is not None and first_doc.get("is_doctor") is not None and first_doc.get("device_sectors") is not None:
        return data

    try:
        raw_dir = os.path.join(batch_dir, "raw")
        raw_masters = [os.path.join(raw_dir, f) for f in os.listdir(raw_dir) if f.endswith(('.xlsx', '.xls')) and "AuthLog" not in f] if os.path.exists(raw_dir) else []
        if not raw_masters:
            defaults = get_default_docs_files()
            if defaults["master"]:
                raw_masters = [defaults["master"]]

        df_m = load_employee_master(raw_masters) if raw_masters else None
        emp_dict = {}
        if df_m is not None and not df_m.empty:
            df_m['Emp_Code'] = df_m['Emp_Code'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            df_m = df_m.drop_duplicates(subset=['Emp_Code'])
            emp_dict = df_m.set_index('Emp_Code').to_dict('index')

        for d in data["doctors"]:
            code = str(d.get('emp_code', '')).strip()
            m_info = emp_dict.get(code, {})
            sec = str(m_info.get('Dep_ADesc', d.get('sector', ''))).strip()
            job_grp = str(m_info.get('JobGroupName', d.get('job_group', ''))).strip()
            job_ttl = str(d.get('job_title', '')).strip()
            d['sector'] = sec
            d['job_group'] = job_grp
            d['is_doctor'] = is_doctor_title(job_ttl, job_grp)
            if 'device_sectors' not in d or not d['device_sectors']:
                d['device_sectors'] = ['قطاع القاهرة']
            if 'device_locations' not in d or not d['device_locations']:
                d['device_locations'] = ['مستشفى الكهرباء']

        # Save back to processed_data.json
        json_path = os.path.join(batch_dir, "processed_data.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception as err:
        print(f"[BatchManager] Auto-enrichment warning: {err}")

    return data


def get_batch_processed_data(batch_id: str) -> Optional[Dict[str, Any]]:
    """Loads the attendance data for a given batch with auto-enrichment."""
    batch_dir = os.path.join(STORAGE_DIR, batch_id)
    json_path = os.path.join(batch_dir, "processed_data.json")
    if not os.path.exists(json_path):
        return None
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return enrich_batch_processed_data(data, batch_dir)
    except Exception as e:
        print(f"[BatchManager] Error reading batch data {batch_id}: {e}")
        return None


def get_batch_filter_options(batch_id: str) -> Dict[str, Any]:
    """Instant non-blocking retrieval of filter options from json cache with hierarchical support."""
    batch_dir = os.path.join(STORAGE_DIR, batch_id)
    json_path = os.path.join(batch_dir, "filter_options.json")
    opts = {}
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                opts = json.load(f)
        except Exception as e:
            print(f"[BatchManager] Warning reading filter_options.json: {e}")

    # Fallback / extraction if empty
    if not opts:
        processed = get_batch_processed_data(batch_id)
        if processed and "doctors" in processed:
            docs = processed["doctors"]
            departments = sorted(list({d.get("department") for d in docs if d.get("department")}))
            contracts = sorted(list({d.get("contract") for d in docs if d.get("contract")}))
            job_titles = sorted(list({d.get("job_title") for d in docs if d.get("job_title")}))
            opts = {
                "departments": departments,
                "contracts": contracts,
                "job_groups": [],
                "job_titles": job_titles,
                "terminals": [],
                "date_min": None,
                "date_max": None
            }

    # Ensure hierarchical sectors and locations are always present
    if not opts.get("sectors") or not opts.get("locations_by_sector"):
        opts["sectors"] = list(SECTOR_LOCATIONS_MAP.keys())
        opts["locations_by_sector"] = {k: list(v) for k, v in SECTOR_LOCATIONS_MAP.items()}
        all_locs = set()
        for locs in SECTOR_LOCATIONS_MAP.values():
            all_locs.update(locs)
        if opts.get("departments"):
            all_locs.update(opts["departments"])
        opts["locations"] = sorted(list(all_locs))

        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(opts, f, ensure_ascii=False)
        except Exception:
            pass

    return opts


def delete_batch(batch_id: str) -> bool:
    """Deletes a batch directory and removes it from the index."""
    batch_dir = os.path.join(STORAGE_DIR, batch_id)
    if os.path.exists(batch_dir):
        shutil.rmtree(batch_dir, ignore_errors=True)

    index = load_batches_index()
    new_index = [b for b in index if b["id"] != batch_id]
    save_batches_index(new_index)
    return True


def reprocess_batch(batch_id: str) -> Dict[str, Any]:
    """
    Re-runs the shift engine on the existing raw files of a batch and overwrites
    processed_data.json and filter_options.json. Use this after engine code changes
    to apply fixes without re-uploading files.
    """
    batch_dir = os.path.join(STORAGE_DIR, batch_id)
    if not os.path.exists(batch_dir):
        raise FileNotFoundError(f"Batch {batch_id} not found.")

    raw_dir = os.path.join(batch_dir, "raw")
    output_dir = os.path.join(batch_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    # Identify master and auth files in raw/
    raw_files = sorted([os.path.join(raw_dir, f) for f in os.listdir(raw_dir) if f.endswith(('.xlsx', '.xls'))])
    emp_candidates = [f for f in raw_files if "AuthLog" not in os.path.basename(f)]
    auth_candidates = [f for f in raw_files if "AuthLog" in os.path.basename(f)]

    # Fall back: if naming convention unclear, use all files
    if not auth_candidates:
        auth_candidates = raw_files

    df_master = load_employee_master(emp_candidates if emp_candidates else None)
    df_auth = load_auth_logs(auth_candidates)

    filter_options = get_dynamic_filter_options(df_master, df_auth)
    processed = process_all_doctors(df_master, df_auth, only_with_punches=True)

    # Overwrite processed_data.json and filter_options.json
    processed_json_path = os.path.join(batch_dir, "processed_data.json")
    with open(processed_json_path, "w", encoding="utf-8") as f:
        json.dump(processed, f, ensure_ascii=False)

    filter_options_path = os.path.join(batch_dir, "filter_options.json")
    with open(filter_options_path, "w", encoding="utf-8") as f:
        json.dump(filter_options, f, ensure_ascii=False)

    # Regenerate Excel; delete stale PDF cache
    excel_path = os.path.join(output_dir, "Attendance_Report.xlsx")
    generate_excel_report(processed, excel_path)
    pdf_path = os.path.join(output_dir, "Attendance_Report.pdf")
    if os.path.exists(pdf_path):
        try:
            os.remove(pdf_path)
        except Exception:
            pass

    date_range_str = ""
    if filter_options.get("date_min") and filter_options.get("date_max"):
        date_range_str = f"{filter_options['date_min']} إلى {filter_options['date_max']}"

    # Update index metadata
    index = load_batches_index()
    for b in index:
        if b["id"] == batch_id:
            b["doctors_count"] = len(processed["doctors"])
            b["summary"] = processed["summary"]
            b["date_range"] = date_range_str
            b["last_reprocessed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            break
    save_batches_index(index)

    return next((b for b in index if b["id"] == batch_id), {"id": batch_id})


def init_default_batch_if_empty():
    """If no batches exist yet, initializes the first batch from docs/."""
    index = load_batches_index()
    if index:
        return

    docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs"))
    emp_files = glob.glob(os.path.join(docs_dir, "*بيانات الموظفين*.xlsx"))
    auth_files = sorted(glob.glob(os.path.join(docs_dir, "AuthLogList*.xlsx")))

    if emp_files and auth_files:
        print("[BatchManager] Creating initial default batch from docs/ files...")
        try:
            create_batch(
                batch_name="الدفعة التأسيسية المعتمدة (26 سبتمبر - 18 أكتوبر 2026)",
                master_file_source_path=emp_files[0],
                auth_file_source_paths=auth_files,
                notes="ملفات التشغيل الأصلية لمستشفى الكهرباء / ألماظة"
            )
        except Exception as e:
            print(f"[BatchManager] Initial batch creation failed: {e}")
