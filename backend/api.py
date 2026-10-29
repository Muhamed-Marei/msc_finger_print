# backend/api.py
"""
100% Dynamic FastAPI Backend Service with Batch History & In-Place Editing:
- Batch Management: History of weekly/monthly imports
- Append/Import additional files into existing batch
- Manual In-Place Editing of Doctor Attendance Records
- Dynamic Filter Options per batch
- Real-time recalculation of totals, deficits, and overtimes
- Instant PDF & Excel Export Downloads per batch
"""

import os
import glob
import shutil
import tempfile
import pandas as pd
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, Query, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from .config import (
    DEVICE_LOCATIONS,
    SHIFTS_CONFIG,
    SECTOR_LOCATIONS_MAP,
    FUNCTION_KEY_ACTIONS,
    SHIFT_BUFFER_MINUTES,
    is_doctor_title
)
from .excel_generator import generate_excel_report
from .batch_manager import (
    load_batches_index,
    create_batch,
    append_files_to_batch,
    update_doctor_records,
    get_batch_processed_data,
    get_batch_filter_options,
    delete_batch,
    reprocess_batch,
    init_default_batch_if_empty,
    STORAGE_DIR
)
from .shift_engine import classify_shift, calculate_deficit_and_overtime, minutes_to_hh_mm
from .pdf_generator import generate_pdf_report
from .excel_generator import generate_excel_report

app = FastAPI(title="Fingerprint Intelligence System API with Batch History & Editing", version="3.1.0")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active batch tracking
ACTIVE_STATE = {
    "batch_id": None,
    "processed_data": None,
    "filter_options": {},
}

# Auto-initialize initial batch from docs/ if storage is empty
init_default_batch_if_empty()


def set_active_batch(batch_id: Optional[str] = None):
    """Sets the active batch data in memory."""
    index = load_batches_index()
    if not index:
        ACTIVE_STATE["batch_id"] = None
        ACTIVE_STATE["processed_data"] = None
        ACTIVE_STATE["filter_options"] = {}
        return None

    target_id = batch_id or index[0]["id"]
    batch_meta = next((b for b in index if b["id"] == target_id), None)
    if not batch_meta:
        target_id = index[0]["id"]
        batch_meta = index[0]

    data = get_batch_processed_data(target_id)
    options = get_batch_filter_options(target_id)

    ACTIVE_STATE["batch_id"] = target_id
    ACTIVE_STATE["processed_data"] = data
    ACTIVE_STATE["filter_options"] = options
    return batch_meta


# Set initial active batch
set_active_batch()


class DoctorRecordsUpdateRequest(BaseModel):
    records: List[Dict[str, Any]]


# ==========================================================
# BATCHES ENDPOINTS
# ==========================================================

@app.get("/api/batches")
def list_batches():
    """Lists all historical import batches with creation date and time."""
    index = load_batches_index()
    return {
        "active_batch_id": ACTIVE_STATE["batch_id"],
        "batches": index
    }


@app.get("/api/shifts")
def get_shifts_config():
    """Returns all shift definitions, function keys actions, and buffer rules."""
    return {
        "shifts": SHIFTS_CONFIG,
        "function_keys": FUNCTION_KEY_ACTIONS,
        "buffer_minutes": SHIFT_BUFFER_MINUTES
    }


from .data_loader import (
    load_employee_master,
    load_auth_logs,
    get_dynamic_filter_options,
    normalize_text
)


@app.post("/api/batches")
async def create_new_batch(
    batch_name: Optional[str] = Form(None, description="Name or title for this import batch"),
    notes: Optional[str] = Form(None),
    master_files: Optional[List[UploadFile]] = File(None, description="One or more Employee Master Excel Files"),
    master_file: Optional[UploadFile] = File(None, description="Single Employee Master Excel File (backward compatible)"),
    auth_files: Optional[List[UploadFile]] = File(None, description="One or more AuthLogList Excel Files")
):
    """
    Creates a new batch from uploaded files, processes attendance, and persists it.
    Supports multiple employee master files and multiple auth log files.
    Smart schema auto-detection ensures files are classified accurately without error.
    """
    temp_dir = tempfile.mkdtemp()
    try:
        # Collect all master uploads
        all_master_uploads = []
        if master_files:
            all_master_uploads.extend([f for f in master_files if f and f.filename and f.filename.strip()])
        if master_file and master_file.filename and master_file.filename.strip():
            all_master_uploads.append(master_file)

        # Collect all auth uploads
        all_auth_uploads = [f for f in (auth_files or []) if f and f.filename and f.filename.strip()]

        master_temp_paths = []
        auth_temp_paths = []

        # Save and auto-classify master uploads
        for mf in all_master_uploads:
            mf_name = os.path.basename(mf.filename)
            mf_path = os.path.join(temp_dir, mf_name)
            with open(mf_path, "wb") as f:
                shutil.copyfileobj(mf.file, f)
            
            # Check if this file is actually an AuthLog file
            try:
                sample_df = pd.read_excel(mf_path, nrows=2)
                cols = [str(c).strip() for c in sample_df.columns]
                if all(k in cols for k in ['Terminal Name', 'User ID', 'Event Time']):
                    auth_temp_paths.append(mf_path)
                else:
                    master_temp_paths.append(mf_path)
            except Exception:
                master_temp_paths.append(mf_path)

        # Save and auto-classify auth uploads
        for af in all_auth_uploads:
            af_name = os.path.basename(af.filename)
            af_path = os.path.join(temp_dir, af_name)
            with open(af_path, "wb") as f:
                shutil.copyfileobj(af.file, f)

            try:
                sample_df = pd.read_excel(af_path, nrows=2)
                cols = [str(c).strip() for c in sample_df.columns]
                if all(k in cols for k in ['Terminal Name', 'User ID', 'Event Time']):
                    auth_temp_paths.append(af_path)
                else:
                    master_temp_paths.append(af_path)
            except Exception:
                auth_temp_paths.append(af_path)

        meta = create_batch(
            batch_name=batch_name,
            master_file_source_paths=master_temp_paths if master_temp_paths else None,
            auth_file_source_paths=auth_temp_paths if auth_temp_paths else None,
            notes=notes
        )

        set_active_batch(meta["id"])

        return {
            "success": True,
            "message": f"تم استيراد الدفعة '{meta['name']}' بنجاح وحفظها في الأرشيف.",
            "batch": meta
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"فشل إنشاء الدفعة: {str(e)}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@app.post("/api/batches/{batch_id}/append-files")
async def append_files(
    batch_id: str,
    auth_files: Optional[List[UploadFile]] = File(None, description="Additional AuthLogList Excel Files"),
    master_files: Optional[List[UploadFile]] = File(None, description="Optional updated master files"),
    master_file: Optional[UploadFile] = File(None, description="Optional single updated master file")
):
    """
    Appends new auth log files and/or updated master employee files to an existing batch.
    Includes smart schema auto-detection and instantly updates active in-memory state.
    """
    temp_dir = tempfile.mkdtemp()
    try:
        all_master_uploads = []
        if master_files:
            all_master_uploads.extend([f for f in master_files if f and f.filename and f.filename.strip()])
        if master_file and master_file.filename and master_file.filename.strip():
            all_master_uploads.append(master_file)

        all_auth_uploads = [f for f in (auth_files or []) if f and f.filename and f.filename.strip()]

        if not all_auth_uploads and not all_master_uploads:
            raise HTTPException(status_code=400, detail="لم يتم تزويد أي ملفات للإلحاق بالدفعة.")

        master_temp_paths = []
        for mf in all_master_uploads:
            mf_name = os.path.basename(mf.filename)
            mf_path = os.path.join(temp_dir, mf_name)
            with open(mf_path, "wb") as f:
                shutil.copyfileobj(mf.file, f)
            master_temp_paths.append(mf_path)

        auth_temp_paths = []
        for af in all_auth_uploads:
            af_name = os.path.basename(af.filename)
            af_path = os.path.join(temp_dir, af_name)
            with open(af_path, "wb") as f:
                shutil.copyfileobj(af.file, f)

            # Auto-classify in case user accidentally selected master file as auth file
            try:
                sniff_df = pd.read_excel(af_path, nrows=3)
                sniff_cols = [str(c).strip().lower() for c in sniff_df.columns]
                if any(c in sniff_cols for c in ['emp_code', 'كود الموظف', 'emp code', 'الادارة', 'العقد']):
                    master_temp_paths.append(af_path)
                else:
                    auth_temp_paths.append(af_path)
            except Exception:
                auth_temp_paths.append(af_path)

        updated_meta = append_files_to_batch(
            batch_id=batch_id,
            new_auth_file_paths=auth_temp_paths if auth_temp_paths else [],
            new_master_file_paths=master_temp_paths if master_temp_paths else None
        )

        # Refresh active state immediately
        set_active_batch(batch_id)

        total_added = len(auth_temp_paths) + len(master_temp_paths)
        return {
            "success": True,
            "message": f"تم دمج {total_added} ملف في الدفعة '{updated_meta['name']}' بنجاح وتحديث الكشوفات.",
            "batch": updated_meta
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"فشل دمج الملفات: {str(e)}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@app.post("/api/batches/{batch_id}/reprocess")
async def reprocess_batch_endpoint(batch_id: str):
    """
    Re-runs the shift engine on the existing raw files of a batch.
    Use this after engine code fixes to update processed data without re-uploading files.
    """
    try:
        updated_meta = reprocess_batch(batch_id)
        # Refresh in-memory active state
        set_active_batch(batch_id)
        return {
            "success": True,
            "message": f"تمت إعادة معالجة الدفعة بنجاح بالمحرك المحدَّث.",
            "batch": updated_meta
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"فشل إعادة المعالجة: {str(e)}")


@app.post("/api/batches/{batch_id}/activate")
def activate_batch(batch_id: str):
    """Switches the active working batch."""
    meta = set_active_batch(batch_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Batch not found.")
    return {
        "success": True,
        "active_batch": meta
    }


@app.delete("/api/batches/{batch_id}")
def remove_batch(batch_id: str):
    """Deletes a batch and updates history."""
    delete_batch(batch_id)
    set_active_batch()
    return {
        "success": True,
        "message": f"تم حذف الدفعة {batch_id} بنجاح."
    }


# ==========================================================
# ATTENDANCE EDITING & DOCTOR DETAILS
# ==========================================================

@app.put("/api/batches/{batch_id}/doctors/{emp_code}")
def edit_doctor_records(
    batch_id: str,
    emp_code: str,
    payload: DoctorRecordsUpdateRequest
):
    """
    Saves in-place user manual modifications to a doctor's attendance records,
    recalculates totals, and updates the batch PDF and Excel exports.
    """
    try:
        res = update_doctor_records(
            batch_id=batch_id,
            emp_code=emp_code,
            updated_records=payload.records
        )
        if ACTIVE_STATE["batch_id"] == batch_id:
            set_active_batch(batch_id)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"فشل حفظ التعديلات: {str(e)}")


@app.get("/api/doctors/{emp_code}")
def get_doctor_detail(emp_code: str, batch_id: Optional[str] = None):
    if batch_id and batch_id != ACTIVE_STATE["batch_id"]:
        set_active_batch(batch_id)

    if not ACTIVE_STATE["processed_data"]:
        raise HTTPException(status_code=400, detail="No batch data available.")

    doc = next((d for d in ACTIVE_STATE["processed_data"]["doctors"] if d['emp_code'] == emp_code.strip()), None)
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found in this batch.")
    return doc


@app.get("/api/summary")
def get_summary(batch_id: Optional[str] = None):
    if batch_id and batch_id != ACTIVE_STATE["batch_id"]:
        set_active_batch(batch_id)

    if not ACTIVE_STATE["processed_data"]:
        raise HTTPException(status_code=400, detail="No batch data available.")
    return ACTIVE_STATE["processed_data"]["summary"]


def apply_doctor_filters(
    docs: List[Dict[str, Any]],
    search: Optional[str] = None,
    dept: Optional[str] = None,
    sector: Optional[str] = None,
    location: Optional[str] = None,
    jobs: Optional[List[str]] = None,
    job: Optional[str] = None,
    only_doctors: Optional[bool] = False
) -> List[Dict[str, Any]]:
    """Robust multi-dimensional filtering for doctors and staff."""
    filtered = list(docs)

    # 1. Search Query (Code, Name, Job, Department, Sector)
    if search:
        norm_q = normalize_text(search)
        filtered = [
            d for d in filtered
            if norm_q in normalize_text(d.get('emp_code', ''))
            or norm_q in normalize_text(d.get('emp_name', ''))
            or norm_q in normalize_text(d.get('job_title', ''))
            or norm_q in normalize_text(d.get('department', ''))
            or norm_q in normalize_text(d.get('sector', ''))
        ]

    # 2. Sector Filter (القطاع)
    if sector and sector.strip() and sector.strip() not in ["جميع القطاعات", "الكل"]:
        norm_sec = normalize_text(sector)
        def matches_sector(d):
            d_sec = normalize_text(d.get('sector', ''))
            d_dept = normalize_text(d.get('department', ''))
            d_dev_secs = [normalize_text(s) for s in d.get('device_sectors', [])]
            return norm_sec in d_sec or any(norm_sec in ds for ds in d_dev_secs) or norm_sec in d_dept
        filtered = [d for d in filtered if matches_sector(d)]

    # 3. Location Filter (المكان)
    if location and location.strip() and location.strip() not in ["جميع الأماكن", "الكل"]:
        norm_loc = normalize_text(location)
        def matches_loc(d):
            d_dept = normalize_text(d.get('department', ''))
            d_sec = normalize_text(d.get('sector', ''))
            d_dev_locs = [normalize_text(l) for l in d.get('device_locations', [])]
            return norm_loc in d_dept or any(norm_loc in dl for dl in d_dev_locs) or norm_loc in d_sec
        filtered = [d for d in filtered if matches_loc(d)]

    # 4. Department Filter (backward compat)
    if dept and dept.strip() and dept.strip() not in ["جميع الأقسام", "الكل"]:
        norm_dept = normalize_text(dept)
        filtered = [
            d for d in filtered
            if norm_dept in normalize_text(d.get('department', ''))
            or norm_dept in normalize_text(d.get('sector', ''))
        ]

    # 5. Multiple Job Titles Filter (الوظيفة)
    selected_jobs = []
    if jobs:
        for j in jobs:
            if j:
                for item in str(j).split(','):
                    it = item.strip()
                    if it and it not in ["الكل", "جميع الوظائف"]:
                        selected_jobs.append(normalize_text(it))
    if job and job.strip() and job.strip() not in ["الكل", "جميع الوظائف"]:
        for item in str(job).split(','):
            it = item.strip()
            if it:
                selected_jobs.append(normalize_text(it))

    if selected_jobs:
        valid_jobs = {sj for sj in selected_jobs if sj}
        if valid_jobs:
            filtered = [
                d for d in filtered
                if any(sj == normalize_text(d.get('job_title', '')) or sj in normalize_text(d.get('job_title', '')) for sj in valid_jobs)
            ]

    # 6. Only Doctors Filter (الأطباء فقط)
    if only_doctors:
        filtered = [
            d for d in filtered
            if d.get('is_doctor') is True or is_doctor_title(d.get('job_title', ''), d.get('job_group', ''))
        ]

    return filtered


@app.get("/api/filter-options")
def get_filter_options(batch_id: Optional[str] = None):
    target_id = batch_id or ACTIVE_STATE["batch_id"]
    if not target_id:
        return {
            "sectors": list(SECTOR_LOCATIONS_MAP.keys()),
            "locations_by_sector": {k: list(v) for k, v in SECTOR_LOCATIONS_MAP.items()},
            "locations": [],
            "departments": [],
            "contracts": [],
            "job_groups": [],
            "job_titles": [],
            "doctor_job_titles": [],
            "terminals": [],
            "date_min": None,
            "date_max": None
        }

    return get_batch_filter_options(target_id)


@app.get("/api/doctors")
def get_doctors(
    batch_id: Optional[str] = None,
    search: Optional[str] = Query(None, description="Search by Name or Code"),
    dept: Optional[str] = Query(None, description="Filter by Department"),
    sector: Optional[str] = Query(None, description="Filter by Sector (القطاع)"),
    location: Optional[str] = Query(None, description="Filter by Location (المكان)"),
    jobs: Optional[List[str]] = Query(None, description="Filter by multiple Job Titles (الوظيفة)"),
    job: Optional[str] = Query(None, description="Filter by single Job Title"),
    only_doctors: Optional[bool] = Query(False, description="Filter only Doctors/Medical staff"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    if batch_id and batch_id != ACTIVE_STATE["batch_id"]:
        set_active_batch(batch_id)

    if not ACTIVE_STATE["processed_data"]:
        return {"total": 0, "offset": offset, "limit": limit, "doctors": []}

    all_docs = ACTIVE_STATE["processed_data"]["doctors"]
    docs = apply_doctor_filters(
        docs=all_docs,
        search=search,
        dept=dept,
        sector=sector,
        location=location,
        jobs=jobs,
        job=job,
        only_doctors=only_doctors
    )

    total = len(docs)
    paginated = docs[offset: offset + limit]

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "doctors": [
            {
                "emp_code": d['emp_code'],
                "emp_name": d['emp_name'],
                "job_title": d['job_title'],
                "department": d['department'],
                "sector": d.get('sector', ''),
                "is_doctor": d.get('is_doctor', False),
                "device_locations": d.get('device_locations', []),
                "contract": d['contract'],
                "total_days_worked": d['total_days_worked'],
                "total_time_spent": d['total_time_spent'],
                "total_deficit": d['total_deficit'],
                "total_overtime": d['total_overtime'],
                "records_count": len(d['records'])
            }
            for d in paginated
        ]
    }


# ==========================================================
# EXPORTS ENDPOINTS
# ==========================================================

@app.get("/api/export/excel")
def export_excel(
    batch_id: Optional[str] = None,
    doctor_code: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    dept: Optional[str] = Query(None),
    sector: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    jobs: Optional[List[str]] = Query(None),
    job: Optional[str] = Query(None),
    only_doctors: Optional[bool] = Query(False)
):
    target_id = batch_id or ACTIVE_STATE["batch_id"]
    if not target_id:
        raise HTTPException(status_code=400, detail="No active batch.")

    data = get_batch_processed_data(target_id)
    if not data:
        raise HTTPException(status_code=404, detail="Batch data not found.")

    if doctor_code:
        single_doc = [d for d in data["doctors"] if d['emp_code'] == doctor_code.strip()]
        if not single_doc:
            raise HTTPException(status_code=404, detail="Doctor code not found.")
        temp_excel = tempfile.mktemp(suffix=".xlsx")
        generate_excel_report({"doctors": single_doc, "summary": data["summary"]}, temp_excel)
        return FileResponse(
            temp_excel,
            filename=f"Doctor_{doctor_code}_Attendance.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    has_filters = any([search, dept, sector, location, jobs, job, only_doctors])
    if has_filters:
        filtered_docs = apply_doctor_filters(
            docs=data["doctors"],
            search=search,
            dept=dept,
            sector=sector,
            location=location,
            jobs=jobs,
            job=job,
            only_doctors=only_doctors
        )
        total_time_spent = sum(d.get('total_time_spent_minutes', 0) for d in filtered_docs)
        total_deficit = sum(d.get('total_deficit_minutes', 0) for d in filtered_docs)
        total_overtime = sum(d.get('total_overtime_minutes', 0) for d in filtered_docs)
        filtered_summary = {
            "total_doctors": len(filtered_docs),
            "total_hours": minutes_to_hh_mm(total_time_spent),
            "total_deficit": minutes_to_hh_mm(total_deficit),
            "total_overtime": minutes_to_hh_mm(total_overtime)
        }
        temp_excel = tempfile.mktemp(suffix=".xlsx")
        generate_excel_report({"doctors": filtered_docs, "summary": filtered_summary}, temp_excel)
        return FileResponse(
            temp_excel,
            filename=f"Doctor_Attendance_{target_id}_filtered.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    excel_file = os.path.join(STORAGE_DIR, target_id, "output", "Attendance_Report.xlsx")
    if not os.path.exists(excel_file):
        generate_excel_report(data, excel_file)

    filename = f"Doctor_Attendance_{target_id}.xlsx"
    return FileResponse(
        excel_file,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@app.get("/api/export/pdf")
def export_pdf(
    batch_id: Optional[str] = None,
    doctor_code: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    dept: Optional[str] = Query(None),
    sector: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    jobs: Optional[List[str]] = Query(None),
    job: Optional[str] = Query(None),
    only_doctors: Optional[bool] = Query(False)
):
    target_id = batch_id or ACTIVE_STATE["batch_id"]
    if not target_id:
        raise HTTPException(status_code=400, detail="No active batch.")

    data = get_batch_processed_data(target_id)
    if not data:
        raise HTTPException(status_code=404, detail="Batch data not found.")

    if doctor_code:
        single_doc = [d for d in data["doctors"] if d['emp_code'] == doctor_code.strip()]
        if not single_doc:
            raise HTTPException(status_code=404, detail="Doctor code not found.")
        
        temp_pdf = tempfile.mktemp(suffix=".pdf")
        generate_pdf_report({"doctors": single_doc, "summary": data["summary"]}, temp_pdf)
        return FileResponse(
            temp_pdf,
            filename=f"Doctor_{doctor_code}_Attendance.pdf",
            media_type="application/pdf"
        )

    has_filters = any([search, dept, sector, location, jobs, job, only_doctors])
    if has_filters:
        filtered_docs = apply_doctor_filters(
            docs=data["doctors"],
            search=search,
            dept=dept,
            sector=sector,
            location=location,
            jobs=jobs,
            job=job,
            only_doctors=only_doctors
        )
        total_time_spent = sum(d.get('total_time_spent_minutes', 0) for d in filtered_docs)
        total_deficit = sum(d.get('total_deficit_minutes', 0) for d in filtered_docs)
        total_overtime = sum(d.get('total_overtime_minutes', 0) for d in filtered_docs)
        filtered_summary = {
            "total_doctors": len(filtered_docs),
            "total_hours": minutes_to_hh_mm(total_time_spent),
            "total_deficit": minutes_to_hh_mm(total_deficit),
            "total_overtime": minutes_to_hh_mm(total_overtime)
        }
        temp_pdf = tempfile.mktemp(suffix=".pdf")
        generate_pdf_report({"doctors": filtered_docs, "summary": filtered_summary}, temp_pdf)
        return FileResponse(
            temp_pdf,
            filename=f"Doctors_Attendance_{target_id}_filtered.pdf",
            media_type="application/pdf"
        )

    pdf_file = os.path.join(STORAGE_DIR, target_id, "output", "Attendance_Report.pdf")
    if not os.path.exists(pdf_file):
        generate_pdf_report(data, pdf_file)

    filename = f"Doctors_Attendance_{target_id}.pdf"
    return FileResponse(
        pdf_file,
        filename=filename,
        media_type="application/pdf"
    )
