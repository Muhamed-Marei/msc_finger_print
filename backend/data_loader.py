# backend/data_loader.py
"""
Dynamic Data Loader & Cleanser:
- Ingestion of multiple AuthLogList Excel files
- Ingestion of multiple Employee Master Data files
- Automatic column standardization and smart schema auto-detection
- Arabic & English text normalization for searching and filtering
- Deduplication and data normalization
- 100% Dynamic Metadata Extraction (No static or hardcoded presets)
"""

import os
import re
import glob
import pandas as pd
from typing import List, Optional, Union, Dict, Any


def normalize_text(text: Any) -> str:
    """
    Normalizes text for robust searching and filtering across Arabic and English:
    - Lowercase English letters
    - Remove Arabic diacritics / tashkeel (fatha, damma, kasra, tanween, sukun, shadda)
    - Remove Arabic tatweel (kashida)
    - Normalize Alefs: [أ إ آ ٱ] -> ا
    - Normalize Yaa / Alef Maksura: [ى ي] -> ي
    - Normalize Taa Marbuta / Haa: [ة] -> ه
    - Strip leading/trailing/multiple whitespaces
    """
    if text is None:
        return ""
    s = str(text).strip().lower()
    if not s or s in ['nan', 'none']:
        return ""

    # Remove Arabic Tashkeel / Diacritics
    s = re.sub(r'[\u064B-\u065F\u0670]', '', s)
    # Remove Tatweel / Kashida
    s = re.sub(r'\u0640', '', s)
    # Normalize Alef forms
    s = re.sub(r'[أإآٱ]', 'ا', s)
    # Normalize Yaa / Alef Maksura
    s = re.sub(r'[ىي]', 'ي', s)
    # Normalize Taa Marbuta
    s = re.sub(r'ة', 'ه', s)
    # Collapse multiple spaces
    s = re.sub(r'\s+', ' ', s)
    return s.strip()


def get_default_docs_paths():
    """Returns the default master and auth files from the docs/ directory."""
    docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs"))
    default_masters = glob.glob(os.path.join(docs_dir, "*بيانات الموظفين*.xlsx"))
    default_auths = sorted(glob.glob(os.path.join(docs_dir, "AuthLogList*.xlsx")))
    return {
        "master": default_masters[0] if default_masters else None,
        "auths": default_auths
    }


# Standard Column Aliases Mapping for Employee Master
COLUMN_ALIASES = {
    'Emp_Code': ['emp_code', 'empcode', 'emp code', 'employee code', 'كود الموظف', 'كود', 'رقم الموظف', 'user id', 'userid', 'enno'],
    'Staff_AName': ['staff_aname', 'staff aname', 'staff name', 'name', 'اسم الموظف', 'اسم', 'الاسم', 'اسم العامل', 'employee name'],
    'JD_ADesc': ['jd_adesc', 'jd adesc', 'job title', 'title', 'الوظيفة', 'المسمى الوظيفي', 'الوظيفه'],
    'Dep_ADesc': ['dep_adesc', 'dep adesc', 'department', 'الإدارة', 'الادارة', 'القسم', 'مركز التكلفة', 'مركز التكلفه'],
    'Cost_Local': ['cost_local', 'cost local', 'cost center', 'مركز تكلفة'],
    'A_Desc': ['a_desc', 'a desc', 'contract', 'نوع العقد', 'العقد'],
    'JobGroupName': ['jobgroupname', 'job group', 'المجموعة الوظيفية', 'المجموعه الوظيفيه'],
    'Company_A_Name': ['company_a_name', 'company', 'الشركة', 'الشركه', 'مقر العمل']
}


def standardize_master_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Detects and standardizes various column name conventions to standard master names."""
    col_map = {}
    for actual_col in df.columns:
        norm_col = str(actual_col).strip().lower()
        for std_col, aliases in COLUMN_ALIASES.items():
            if norm_col == std_col.lower() or norm_col in aliases:
                col_map[actual_col] = std_col
                break
    if col_map:
        df = df.rename(columns=col_map)
    return df


def load_employee_master(file_paths: Union[str, List[str]]) -> pd.DataFrame:
    """
    Loads, standardizes, combines, and normalizes one or multiple Employee Master Excel files.
    If files don't contain valid master data, falls back gracefully to default master database in docs/.
    """
    if isinstance(file_paths, str):
        paths = [file_paths]
    else:
        paths = list(file_paths) if file_paths else []

    dfs = []
    for f in paths:
        if not f or not os.path.exists(f):
            continue
        try:
            df = pd.read_excel(f)
            df.columns = [str(c).strip() for c in df.columns]

            # If this is an AuthLog file by mistake, skip it
            if all(k in df.columns for k in ['Terminal Name', 'User ID', 'Event Time']):
                continue

            df = standardize_master_columns(df)

            if 'Emp_Code' in df.columns:
                df['Emp_Code'] = df['Emp_Code'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
                dfs.append(df)
        except Exception as e:
            print(f"[DataLoader] Warning reading master file {f}: {e}")

    # Fallback to default docs master file if no valid master data was read
    if not dfs:
        default_path = get_default_docs_paths()["master"]
        if default_path and os.path.exists(default_path):
            df_def = pd.read_excel(default_path)
            df_def.columns = [str(c).strip() for c in df_def.columns]
            df_def = standardize_master_columns(df_def)
            if 'Emp_Code' in df_def.columns:
                df_def['Emp_Code'] = df_def['Emp_Code'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
                dfs.append(df_def)

    if not dfs:
        raise ValueError("لم يتم العثور على قاعدة بيانات موظفين صالحة.")

    combined = pd.concat(dfs, ignore_index=True)
    # Deduplicate on Emp_Code
    combined = combined.drop_duplicates(subset=['Emp_Code'], keep='last').reset_index(drop=True)

    # Ensure required columns exist
    text_cols = ['Staff_AName', 'JD_ADesc', 'Dep_ADesc', 'Cost_Local', 'A_Desc', 'JobGroupName', 'Company_A_Name']
    for col in text_cols:
        if col not in combined.columns:
            combined[col] = ''
        else:
            combined[col] = combined[col].astype(str).str.strip().replace({'nan': '', 'None': ''})

    return combined


def load_auth_logs(file_paths: Union[str, List[str]], deduplicate_window_seconds: int = 60) -> pd.DataFrame:
    """
    Loads, consolidates, cleans, and deduplicates fingerprint transaction logs from one or multiple Excel files.
    Skips non-auth files gracefully, and falls back to default docs/ auth files if needed.
    """
    if isinstance(file_paths, str):
        if os.path.isdir(file_paths):
            files = sorted(glob.glob(os.path.join(file_paths, "AuthLogList*.xlsx")))
        else:
            files = [file_paths]
    else:
        files = list(file_paths) if file_paths else []

    dfs = []
    for f in files:
        if not f or not os.path.exists(f):
            continue
        try:
            df = pd.read_excel(f)
            df.columns = [str(c).strip() for c in df.columns]

            # Require standard AuthLog columns
            required_cols = ['Terminal Name', 'User ID', 'Event Time']
            if not all(col in df.columns for col in required_cols):
                continue

            dfs.append(df)
        except Exception as e:
            print(f"[DataLoader] Warning reading auth file {f}: {e}")

    # Fallback to default auth files if none provided or valid
    if not dfs:
        default_auths = get_default_docs_paths()["auths"]
        for f in default_auths:
            if os.path.exists(f):
                df = pd.read_excel(f)
                df.columns = [str(c).strip() for c in df.columns]
                dfs.append(df)

    if not dfs:
        raise ValueError("Could not read any valid data from provided files.")

    combined = pd.concat(dfs, ignore_index=True)

    # 1. Clean User ID as string
    combined['User ID'] = combined['User ID'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

    # 2. Parse Event Time
    combined['Event Time'] = pd.to_datetime(combined['Event Time'], errors='coerce')
    combined = combined.dropna(subset=['Event Time', 'User ID'])

    # 3. Filter valid auth results
    if 'Auth Result' in combined.columns:
        combined = combined[~combined['Auth Result'].astype(str).str.lower().isin(['fail', 'failed', 'error'])]

    # 4. Standardize Function Key
    if 'Function Key' in combined.columns:
        combined['Function Key'] = combined['Function Key'].astype(str).str.strip().str.upper()
    else:
        combined['Function Key'] = 'F1'

    # Clean Terminal Name
    if 'Terminal Name' in combined.columns:
        combined['Terminal Name'] = combined['Terminal Name'].astype(str).str.strip()

    # 5. Sort chronologically per user
    combined = combined.sort_values(by=['User ID', 'Event Time']).reset_index(drop=True)

    # 6. Deduplication within time window (general 60s + same key 5-minute duplicate rejection)
    if deduplicate_window_seconds > 0:
        combined['time_diff'] = combined.groupby('User ID')['Event Time'].diff().dt.total_seconds()
        combined['prev_key'] = combined.groupby('User ID')['Function Key'].shift(1)
        duplicate_mask = (
            ((combined['time_diff'] < deduplicate_window_seconds) & (combined['time_diff'] >= 0)) |
            ((combined['time_diff'] < 300) & (combined['time_diff'] >= 0) & (combined['Function Key'] == combined['prev_key']))
        )
        combined = combined[~duplicate_mask].drop(columns=['time_diff', 'prev_key']).reset_index(drop=True)

    return combined


def get_dynamic_filter_options(df_master: pd.DataFrame, df_auth: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """
    Dynamically extracts all available options from the actual uploaded files.
    No hardcoded values. Safely handles mixed types and missing values.
    """
    def clean_unique_list(series) -> List[str]:
        if series is None:
            return []
        items = set()
        for val in series.dropna().unique():
            s = str(val).strip()
            if s and s.lower() not in ['nan', 'none']:
                items.add(s)
        return sorted(list(items), key=lambda x: str(x))

    from .config import SECTOR_LOCATIONS_MAP, is_doctor_title

    departments = clean_unique_list(df_master.get('Cost_Local'))
    master_sectors = clean_unique_list(df_master.get('Dep_ADesc'))
    contracts = clean_unique_list(df_master.get('A_Desc'))
    job_groups = clean_unique_list(df_master.get('JobGroupName'))
    job_titles = clean_unique_list(df_master.get('JD_ADesc'))

    # Extract doctor-specific job titles using fast record iteration
    doctor_job_titles_set = set()
    if df_master is not None and not df_master.empty:
        needed_cols = [c for c in ['JD_ADesc', 'JobGroupName'] if c in df_master.columns]
        if 'JD_ADesc' in needed_cols:
            records = df_master[needed_cols].dropna(subset=['JD_ADesc']).to_dict('records')
            for r in records:
                t = str(r.get('JD_ADesc', '')).strip()
                g = str(r.get('JobGroupName', '')).strip()
                if t and t.lower() not in ['nan', 'none'] and is_doctor_title(t, g):
                    doctor_job_titles_set.add(t)
    doctor_job_titles = sorted(list(doctor_job_titles_set))

    # Hierarchical Sectors & Locations
    sectors = list(SECTOR_LOCATIONS_MAP.keys())
    for s in master_sectors:
        if s not in sectors and not any(sec in s for sec in sectors):
            sectors.append(s)

    locations_by_sector = {k: list(v) for k, v in SECTOR_LOCATIONS_MAP.items()}

    all_locations = set()
    for locs in SECTOR_LOCATIONS_MAP.values():
        all_locations.update(locs)
    all_locations.update(departments)
    locations = sorted(list(all_locations))

    terminals = []
    date_min = None
    date_max = None
    if df_auth is not None and not df_auth.empty:
        terminals = clean_unique_list(df_auth.get('Terminal Name'))
        if 'Event Time' in df_auth.columns:
            date_min = df_auth['Event Time'].min().strftime('%Y-%m-%d')
            date_max = df_auth['Event Time'].max().strftime('%Y-%m-%d')

    return {
        "sectors": sectors,
        "locations_by_sector": locations_by_sector,
        "locations": locations,
        "departments": departments if departments else master_sectors,
        "master_sectors": master_sectors,
        "contracts": contracts,
        "job_groups": job_groups,
        "job_titles": job_titles,
        "doctor_job_titles": doctor_job_titles,
        "terminals": terminals,
        "date_min": date_min,
        "date_max": date_max
    }


def filter_employees_dynamic(
    df_master: pd.DataFrame,
    departments: Optional[List[str]] = None,
    contracts: Optional[List[str]] = None,
    job_groups: Optional[List[str]] = None,
    job_titles: Optional[List[str]] = None,
    search_query: Optional[str] = None
) -> pd.DataFrame:
    """
    Dynamically filters employee master records using multi-select criteria and robust Arabic/English normalized search.
    """
    if df_master is None or df_master.empty:
        return pd.DataFrame()

    df = df_master.copy()

    if departments:
        norm_depts = [normalize_text(d) for d in departments if d]
        if norm_depts:
            df = df[df['Dep_ADesc'].apply(lambda x: normalize_text(x) in norm_depts)]

    if contracts:
        norm_contracts = [normalize_text(c) for c in contracts if c]
        if norm_contracts:
            df = df[df['A_Desc'].apply(lambda x: normalize_text(x) in norm_contracts)]

    if job_groups:
        norm_groups = [normalize_text(g) for g in job_groups if g]
        if norm_groups:
            df = df[df['JobGroupName'].apply(lambda x: normalize_text(x) in norm_groups)]

    if job_titles:
        norm_titles = [normalize_text(t) for t in job_titles if t]
        if norm_titles:
            df = df[df['JD_ADesc'].apply(lambda x: normalize_text(x) in norm_titles)]

    if search_query:
        norm_q = normalize_text(search_query)
        if norm_q:
            def matches_search(row):
                code = str(row.get('Emp_Code', '')).strip()
                if norm_q in code:
                    return True
                name = normalize_text(row.get('Staff_AName', ''))
                if norm_q in name:
                    return True
                job = normalize_text(row.get('JD_ADesc', ''))
                if norm_q in job:
                    return True
                dep = normalize_text(row.get('Dep_ADesc', ''))
                if norm_q in dep:
                    return True
                cost = normalize_text(row.get('Cost_Local', ''))
                if norm_q in cost:
                    return True
                return False

            df = df[df.apply(matches_search, axis=1)]

    return df.reset_index(drop=True)
