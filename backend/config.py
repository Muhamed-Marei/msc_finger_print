# backend/config.py
"""
Configuration definitions for Fingerprint System:
- Terminal & Device Locations mapping
- Shift windows, targets, and rules
- Function Key definitions
"""

# 1. Device Locations Directory
DEVICE_LOCATIONS = [
    {"sector": "قطاع القاهرة", "location": "مستشفى الكهرباء", "id": 1, "name": "MSC-F1"},
    {"sector": "قطاع القاهرة", "location": "مستشفى الكهرباء", "id": 2, "name": "MSC-B1-01"},
    {"sector": "قطاع القاهرة", "location": "مستشفى الكهرباء", "id": 3, "name": "MSC-B1-02"},
    {"sector": "قطاع القاهرة", "location": "مستشفى الكهرباء", "id": 4, "name": "MSC-B1-03"},
    {"sector": "قطاع القاهرة", "location": "مستشفى الكهرباء", "id": 5, "name": "MSC-F5"},
    {"sector": "قطاع القاهرة", "location": "مقر شركة الخدمات الطبية بالعباسية", "id": 7, "name": "MSC-Abassia-01-Base"},
    {"sector": "قطاع القاهرة", "location": "مقر شركة الخدمات الطبية بالعباسية", "id": 6, "name": "MSC-Abassia-02-F3"},
    {"sector": "قطاع القاهرة", "location": "عيادات روكسي", "id": 21, "name": "MSC-Roksy-01-Pharm"},
    {"sector": "قطاع القاهرة", "location": "عيادات روكسي", "id": 22, "name": "MSC-Roksy-02-Clinic"},
    {"sector": "قطاع القاهرة", "location": "عيادة العباسية (برج مصر للسياحة)", "id": 18, "name": "MSC-Abassia-Clinic"},
    {"sector": "قطاع الجيزة", "location": "مقر القطاع", "id": 8, "name": "MSC-Giza-01-26July"},
    {"sector": "قطاع الجيزة", "location": "مقر القطاع", "id": 9, "name": "MSC-Giza-02-Entag"},
    {"sector": "قطاع الجيزة", "location": "عيادة الإنتاج", "id": 10, "name": "MSC-Giza-03-Dist1"},
    {"sector": "قطاع الجيزة", "location": "عيادات التوزيع", "id": 11, "name": "MSC-Giza -04- Dist2"},
    {"sector": "قطاع الإسكندرية", "location": "مقر رئاسة القطاع", "id": 12, "name": "MSC Alex-01 follow"},
    {"sector": "قطاع الإسكندرية", "location": "مقر رئاسة القطاع", "id": 13, "name": "MSC-Alex-02-Distrib"},
    {"sector": "قطاع الإسكندرية", "location": "العيادات التخصصية جليم", "id": 14, "name": "MSC-Alex-03-Jalim"},
    {"sector": "قطاع الإسكندرية", "location": "مقر الإبراهيمية", "id": 15, "name": "MSC-Alex-04-Ibrahimi"},
    {"sector": "قطاع الإسماعيلية", "location": "مقر القطاع", "id": 27, "name": "MSC-Ismailia-Tahakm"},
    {"sector": "قطاع الإسماعيلية", "location": "مستشفى الإسماعيلية", "id": 23, "name": "MSC-Ismailia-Hospital"},
    {"sector": "قطاع الإسماعيلية", "location": "إنتاج", "id": 28, "name": "MSC-Ismailia-Entag"},
    {"sector": "قطاع الإسماعيلية", "location": "توزيع", "id": 31, "name": "MSC-Ismailia-Dist"},
    {"sector": "قطاع الإسماعيلية", "location": "نقل", "id": 30, "name": "MSC-Ismailia-Naql"},
    {"sector": "قطاع الإسماعيلية", "location": "الوادي الجديد", "id": 32, "name": "MSC-Ismaillia-new-wadi"},
    {"sector": "قطاع المنصورة", "location": "مقر القطاع", "id": 16, "name": "MSC-Mansoura 01 Ma"},
    {"sector": "قطاع المنصورة", "location": "عيادات المنصورة التخصصية", "id": 17, "name": "MSC Mansoura 02-Clinic"},
    {"sector": "قطاع أسيوط", "location": "مقر القطاع", "id": 24, "name": "MSC-Assuit-Maqar"},
    {"sector": "قطاع أسيوط", "location": "عيادات أسيوط التخصصية", "id": 25, "name": "MSC-Assuit-Clinic"},
    {"sector": "قطاع أسيوط", "location": "عيادات المنيا التخصصية", "id": 26, "name": "MSC-Minya-Clinic"},
]

DEVICE_NAME_TO_INFO = {d["name"].strip(): d for d in DEVICE_LOCATIONS}

# Hierarchical Sector -> Locations mapping from device directory
SECTOR_LOCATIONS_MAP = {}
for _item in DEVICE_LOCATIONS:
    _sec = _item["sector"].strip()
    _loc = _item["location"].strip()
    if _sec not in SECTOR_LOCATIONS_MAP:
        SECTOR_LOCATIONS_MAP[_sec] = []
    if _loc not in SECTOR_LOCATIONS_MAP[_sec]:
        SECTOR_LOCATIONS_MAP[_sec].append(_loc)


import re
from typing import Any


def _normalize_title_text(text: Any) -> str:
    if text is None:
        return ""
    s = str(text).strip().lower()
    if not s or s in ['nan', 'none']:
        return ""
    s = re.sub(r'[\u064B-\u065F\u0670]', '', s)  # diacritics
    s = re.sub(r'\u0640', '', s)                 # tatweel
    s = re.sub(r'[أإآٱ]', 'ا', s)                 # alefs
    s = re.sub(r'[ىي]', 'ي', s)                 # yaa
    s = re.sub(r'ة', 'ه', s)                     # taa marbuta
    s = re.sub(r'\s+', ' ', s)                   # whitespace
    return s.strip()


def is_doctor_title(job_title: str = "", job_group: str = "") -> bool:
    """
    Returns True if the job title or job group belongs to medical doctors / physicians / consultants.
    Rigorously eliminates non-medical specialists (IT, HR, admin, nursing, lab/radiology technicians, etc.).
    """
    t = _normalize_title_text(job_title)
    g = _normalize_title_text(job_group)
    if not t and not g:
        return False

    # 1. Explicit non-doctor exclusions (technicians, nurses, admin, IT, finance, logistics, crafts)
    non_doctor_title_words = [
        "فني", "مساعد فني", "معاون", "ملاحظ", "ممرض", "ممرضه", "تمريض",
        "حاسب", "نظم", "كمبيوتر", "برمج", "شبكات",
        "شئون", "شؤون", "اداري", "اداريه", "مكتبي", "مكتبيه",
        "مالي", "ماليه", "حسابات", "محاسب", "خزينه", "مخازن", "مخزن", "مشتريات", "مبيعات",
        "علاقات عامه", "امن", "سلامه", "سائق", "حارس", "عامل", "ترزي", "تمرجي",
        "محامي", "قانوني", "تغذيه", "جوده", "بصريات"
    ]
    has_non_doc_keyword = any(w in t for w in non_doctor_title_words)
    if has_non_doc_keyword and not ("طبيب" in t or "استشاري طبي" in t):
        return False

    # 2. Explicit non-doctor group exclusions
    non_doctor_groups = [
        "المكتبيه", "التنميه الاداريه", "الفنيه", "الهندسيه",
        "الحاسبات", "الخدمات المعاونه", "التمريض", "اخصائي تمريض",
        "التغذيه", "الحرفيه", "الامن"
    ]
    if any(ng in g for ng in non_doctor_groups) and not ("طبيب" in t):
        return False

    # 3. Direct Physician / Doctor Indicators
    if "طبيب" in t or "ممارس عام" in t:
        return True

    # 4. Medical specialties keywords
    medical_specialties = [
        "باطن", "جراح", "اطفال", "تخدير", "رمد", "اشع", "تحاليل", "عظام", "نساء", "توليد",
        "جلد", "قلب", "كلي", "مسالك", "اورام", "اعصاب", "مخ", "انف", "اذن", "اوذن", "صدر",
        "وعائ", "اوعيه", "باثولوج", "الام", "مناظير", "طوارئ", "عنايه", "اسنان"
    ]
    has_med_spec = any(s in t for s in medical_specialties)

    # 5. Consultant, Specialist, Resident, Fellow with verified medical specialty or medical group
    if any(k in t for k in ["استشاري", "استشار", "اخصائي", "اخصائ", "مقيم", "نائب", "زميل"]):
        if has_med_spec:
            return True
        if any(med_g in g for med_g in ["الطب البشري", "المهن الطبيه", "العلاج الطبيعي"]):
            return True

    # 6. Medical group fallback with qualified role
    if any(med_g in g for med_g in ["الطب البشري", "المهن الطبيه"]):
        if any(k in t for k in ["استشاري", "اخصائي", "مقيم", "نائب", "طبيب", "ممارس", "جراح"]):
            return True

    return False


# 2. Shift Definitions and Official Targets (in hours and minutes)
SHIFTS_CONFIG = {
    "A": {
        "name": "صباحي عادي",
        "start": "08:30",
        "end": "14:30",
        "target_hours": 6.0,
        "keys": ["F1", "F2"],
        "description": "من 8:30 ص إلى 2:30 م"
    },
    "B": {
        "name": "مسائي عادي",
        "start": "14:30",
        "end": "20:30",
        "target_hours": 6.0,
        "keys": ["F1", "F2"],
        "description": "من 2:30 م إلى 8:30 م"
    },
    "L": {
        "name": "شفت طويل",
        "start": "08:30",
        "end": "20:30",
        "target_hours": 12.0,
        "keys": ["F1", "F2"],
        "description": "من 8:30 ص إلى 8:30 م"
    },
    "C": {
        "name": "سهر ليلي",
        "start": "20:30",
        "end": "08:30",
        "target_hours": 12.0,
        "keys": ["F3", "F4"],
        "description": "من 8:30 م إلى 8:30 ص اليوم التالي"
    },
    "BC": {
        "name": "مسائي + سهر",
        "start": "14:30",
        "end": "08:30",
        "target_hours": 18.0,
        "keys": ["F1/F3", "F4"],
        "description": "من 2:30 م إلى 8:30 ص اليوم التالي"
    },
    "CA": {
        "name": "سهر + صباحي",
        "start": "20:30",
        "end": "14:30",
        "target_hours": 18.0,
        "keys": ["F3", "F2"],
        "description": "من 8:30 م إلى 2:30 م اليوم التالي"
    },
    "24H": {
        "name": "نوبتجية كاملة",
        "start": "08:30",
        "end": "08:30",
        "target_hours": 24.0,
        "keys": ["F1", "F2", "F3", "F4"],
        "description": "من 8:30 ص إلى 8:30 ص اليوم التالي"
    },
    "24+A": {
        "name": "نوبتجية + صباحي",
        "start": "08:30",
        "end": "14:30",
        "target_hours": 30.0,
        "keys": ["F1", "F2"],
        "spans_days": 2,
        "description": "من 8:30 ص إلى 2:30 م اليوم التالي (30 ساعة)"
    },
    "24+A+B": {
        "name": "نوبتجية + صباحي + مسائي",
        "start": "08:30",
        "end": "20:30",
        "target_hours": 36.0,
        "keys": ["F1", "F2", "F3", "F4"],
        "spans_days": 2,
        "description": "من 8:30 ص إلى 8:30 م اليوم التالي (36 ساعة)"
    }
}

# 3. Minimum duration threshold for valid punch interval (under 40 mins is considered unspecified / غير محدد)
SHORT_PUNCH_MINUTES = 40

# 4. Maximum pairing window (in hours) to accommodate extended shifts (e.g. 24+A+B = 36h + buffer)
MAX_PAIRING_HOURS = 38

# 5. Deduplication window for same function key (seconds)
DEDUP_SAME_KEY_SECONDS = 300  # 5 minutes

# 6. Shift Grace Period / Buffer (minutes)
# Shifts have a 15-minute grace buffer on arrival and departure:
# e.g. Shift A is 8:30 to 2:30 -> allowed window is 8:45 to 2:15.
# After 15 mins (i.e. > 8:45 AM) it is counted as late arrival.
SHIFT_BUFFER_MINUTES = 15

# 7. Function Key Actions and Biometric Meanings Directory
FUNCTION_KEY_ACTIONS = {
    "F1": {
        "key": "F1",
        "action": "تسجيل حضور",
        "action_en": "Check-In",
        "short_action": "حضور",
        "type": "in",
        "badge_color": "#3B82F6"
    },
    "F2": {
        "key": "F2",
        "action": "تسجيل انصراف",
        "action_en": "Check-Out",
        "short_action": "انصراف",
        "type": "out",
        "badge_color": "#10B981"
    },
    "F3": {
        "key": "F3",
        "action": "حضور مسائي / نوبتجية",
        "action_en": "Duty/Night Check-In",
        "short_action": "حضور مسائي",
        "type": "in",
        "badge_color": "#8B5CF6"
    },
    "F4": {
        "key": "F4",
        "action": "انصراف مسائي / نوبتجية",
        "action_en": "Duty/Night Check-Out",
        "short_action": "انصراف مسائي",
        "type": "out",
        "badge_color": "#EC4899"
    }
}
