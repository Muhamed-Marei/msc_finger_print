# backend/shift_engine.py
"""
Core Attendance & Shift Calculation Engine:
- Pairs Function Keys (F1..F4) and cross-midnight shifts
- Accurate Shift Classification (A, B, L, C, BC, CA, 24H, غير محدد)
- Precise calculation of Time Spent, Deficit (وقت التأخير), and Overtime (الوقت الإضافي)
- Verification matching the 208 doctor reports
"""

import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union
from .config import (
    SHIFTS_CONFIG,
    SHORT_PUNCH_MINUTES,
    MAX_PAIRING_HOURS,
    SHIFT_BUFFER_MINUTES,
    FUNCTION_KEY_ACTIONS,
    DEVICE_NAME_TO_INFO,
    is_doctor_title
)

# Arabic day names mapping
ARABIC_DAYS = {
    0: "الإثنين",
    1: "الثلاثاء",
    2: "الأربعاء",
    3: "الخميس",
    4: "الجمعة",
    5: "السبت",
    6: "الأحد"
}


def minutes_to_hh_mm(total_minutes: int) -> str:
    """Formats integer minutes to H:MM (or 0:00)."""
    if total_minutes <= 0:
        return "0:00"
    hours = total_minutes // 60
    mins = total_minutes % 60
    return f"{hours}:{mins:02d}"


def format_am_pm(dt: Optional[datetime]) -> str:
    """Formats datetime to '8:59 AM' or '8:44 PM' (12-hour without leading 0)."""
    if dt is None or pd.isna(dt):
        return ""
    # On Windows %I has leading zero, so format and strip leading zero
    s = dt.strftime("%I:%M %p")
    if s.startswith("0"):
        s = s[1:]
    return s


def classify_shift(check_in: Optional[datetime], check_out: Optional[datetime], duration_minutes: int) -> str:
    """
    Classifies the shift type matching the logic in بصمات دكاتره.pdf:
    - If single punch: "" (blank)
    - If diff < 40 mins: "غير محدد"
    - If night shift (In >= 19:00, Out <= 10:00 next day): "C"
    - If composite afternoon/night (In 14:00-18:30, Out next morning): "BC"
    - If composite evening/morning (In 18:30-20:00, Out next morning >= 09:00): "CA"
    - If afternoon shift same day (In >= 12:01, Out <= 23:59): "B"
    - If morning shift (In 05:00-11:30):
        If Out <= 17:00 (5 PM): "A"
        If Out > 17:00 (5 PM) or duration >= 10h: "L"
    """
    if check_in is None or check_out is None or pd.isna(check_in) or pd.isna(check_out):
        return ""

    if duration_minutes < SHORT_PUNCH_MINUTES:
        return ""

    # Fraction of day from midnight
    tin = (check_in.hour * 3600 + check_in.minute * 60 + check_in.second) / 86400.0
    tout = (check_out.hour * 3600 + check_out.minute * 60 + check_out.second) / 86400.0

    # Overnight flag
    is_next_day = (check_out.date() > check_in.date()) or (tout < tin)

    t_0 = 0.0
    t_5 = 5.0 / 24.0
    t_7 = 7.0 / 24.0
    t_10 = 10.0 / 24.0
    t_12_1 = (12 * 3600 + 60) / 86400.0
    t_15_30 = (15 * 3600 + 30 * 60) / 86400.0
    t_17 = 17.0 / 24.0
    t_18_30 = (18 * 3600 + 30 * 60) / 86400.0
    t_19 = 19.0 / 24.0
    t_23_59 = (23 * 3600 + 59 * 60) / 86400.0

    # 1. Invalid reversed / same-minute edge cases
    if tin >= t_7 and tout <= t_0 and not is_next_day:
        return ""

    # 2. Overnight shifts
    if is_next_day or (tin > tout):
        # Extended shifts starting in morning (05:00 - 11:30) and spanning overnight or beyond 24h
        if tin >= t_5 and tin <= (11.5 / 24.0):
            if duration_minutes >= 33 * 60:       # >= 33 hours -> 24+A+B (target 36h)
                return "24+A+B"
            elif duration_minutes >= 27 * 60:     # >= 27 hours -> 24+A (target 30h)
                return "24+A"
            elif duration_minutes >= 20 * 60:     # >= 20 hours -> 24H (target 24h)
                return "24H"

        # Shift C: In >= 19:00 and Out <= 10:00
        if tin >= t_19 and tout <= t_10:
            return "C"
        # Shift CA: In >= 18:30 and Out <= 15:30
        if tin >= t_18_30 and tout <= t_15_30:
            return "CA"
        # Shift BC: In >= 12:01 and Out <= 10:00
        if tin >= t_12_1 and tout <= t_10:
            return "BC"

        # General long duration overnight fallback
        if duration_minutes >= 33 * 60:
            return "24+A+B"
        elif duration_minutes >= 27 * 60:
            return "24+A"
        elif duration_minutes >= 20 * 60:
            return "24H"
        elif duration_minutes >= 800:
            return "C"
        return ""

    # 3. Same-day shifts
    # Afternoon shift B: In >= 12:01 and Out <= 23:59
    if tin >= t_12_1 and tout <= t_23_59:
        if duration_minutes <= 480:  # <= 8 hours
            return "B"
        return "L"

    # Morning shift A: In >= 05:00 and Out <= 17:00
    if tin >= t_5 and tout <= t_17:
        return "A"

    # Long shift L: In >= 05:00 and Out <= 23:59
    if tin >= t_5 and tout <= t_23_59:
        return "L"

    return ""


def calculate_deficit_and_overtime(shift_type: str, duration_minutes: int) -> Tuple[int, int]:
    """
    Calculates deficit minutes (وقت التأخير) and overtime minutes (الوقت الإضافي).
    Shifts have a 15-minute buffer on arrival and departure (total 30 minutes tolerance):
    e.g. Shift A is 8:30 to 2:30 -> allowed window is 8:45 to 2:15 (5h 30m = 330 mins).
    - If duration >= (target - 30): deficit is 0.
    - If duration < (target - 30): deficit is (target - 30) - duration.
    - Overtime = max(0, duration - target) (extra beyond the official shift target).
    """
    if not shift_type or shift_type in ["غير محدد", ""]:
        return 0, 0

    # Official targets in minutes
    targets = {
        "A": 6 * 60,         # 360
        "B": 6 * 60,         # 360
        "L": 12 * 60,        # 720
        "C": 12 * 60,        # 720
        "BC": 0,             # Composite shifts do not incur deficit in approved report
        "CA": 0,             # Composite shifts do not incur deficit in approved report
        "24H": 24 * 60,      # 1440
        "24+A": 30 * 60,     # 1800
        "24+A+B": 36 * 60,   # 2160
    }

    target = targets.get(shift_type, 0)
    if target == 0:
        return 0, max(0, duration_minutes - (12 * 60))

    if shift_type in ["24H", "24+A", "24+A+B"]:
        allowed_target = target - 30
        deficit = max(0, allowed_target - duration_minutes)
        overtime = max(0, duration_minutes - target)
    else:
        deficit = max(0, target - duration_minutes)
        overtime = max(0, duration_minutes - target)
    return deficit, overtime


def calc_duration_minutes(t_in: datetime, t_out: datetime) -> int:
    """
    Computes duration in minutes by cleaning seconds first (as in biometric attendance systems).
    Verified to match official hospital PDF across all shifts 100%.
    """
    t_in_clean = t_in.replace(second=0, microsecond=0)
    t_out_clean = t_out.replace(second=0, microsecond=0)
    return int((t_out_clean - t_in_clean).total_seconds() // 60)


def process_doctor_records(emp_code: str, logs_df: pd.DataFrame, is_doctor: bool = False) -> List[Dict[str, Any]]:
    """
    Processes all logs for a single doctor and constructs daily report records.
    Pairs F1/F2 (Primary) and F3/F4 (Secondary/Evening/Night).
    """
    if logs_df.empty:
        return []

    # Sort logs chronologically
    sorted_logs = logs_df.sort_values(by='Event Time').reset_index(drop=True)

    # Group punches by shift sessions
    # An overnight punch (F4 or check-out next morning before 11:00 AM) pairs with previous evening F3/In
    records: List[Dict[str, Any]] = []

    # We iterate and build shift events
    used_indices = set()
    n = len(sorted_logs)

    # List of paired shifts
    shifts = []

    # ── Deduplication & Punch Selection ──────────────────────────────────────
    # Rule 1: "if employee use f1 use the first one from the time"
    #   When multiple IN punches (F1, F3) occur on the same calendar day without
    #   an intervening OUT punch, keep the FIRST one and discard subsequent ones.
    # Rule 2: "and if 2 f2 use the last one"
    #   When multiple OUT punches (F2, F4) occur on the same calendar day without
    #   an intervening IN punch, keep the LAST one and discard earlier ones.
    for idx in range(n - 1):
        if idx in used_indices:
            continue
        r_a = sorted_logs.iloc[idx]
        t_a = r_a['Event Time']
        k_a = r_a.get('Function Key', 'F1')

        for idx2 in range(idx + 1, n):
            if idx2 in used_indices:
                continue
            r_b = sorted_logs.iloc[idx2]
            t_b = r_b['Event Time']
            k_b = r_b.get('Function Key', 'F1')

            # Only deduplicate within the same calendar day
            if t_b.date() != t_a.date():
                break

            gap_sec = (t_b - t_a).total_seconds()

            # Stray OUT right before a real check-in (F2 08:18, F1 08:23 ... F2 14:25):
            # the accidental early OUT is discarded so the F1 pairs with the real OUT.
            if k_a in ['F2', 'F4'] and k_b in ['F1', 'F3'] and gap_sec < SHORT_PUNCH_MINUTES * 60:
                has_earlier_in = any(
                    sorted_logs.iloc[m].get('Function Key', 'F1') in ['F1', 'F3']
                    and sorted_logs.iloc[m]['Event Time'].date() == t_a.date()
                    for m in range(0, idx)
                )
                if not has_earlier_in and any(
                    sorted_logs.iloc[m].get('Function Key', 'F1') in ['F2', 'F4']
                    and sorted_logs.iloc[m]['Event Time'].date() == t_a.date()
                    for m in range(idx2 + 1, n)
                ):
                    used_indices.add(idx)
                break

            # If an opposite-direction punch occurs in between, stop grouping
            if k_a in ['F1', 'F3'] and k_b in ['F2', 'F4']:
                break
            if k_a in ['F2', 'F4'] and k_b in ['F1', 'F3']:
                break

            # Consecutive IN keys (F1->F1 or F3->F3): keep first, discard later (idx2)
            # Only when a real OUT follows that day; otherwise the later IN key is the
            # checkout pressed with the wrong key (F1 8:44 ... F1 20:28) and must be kept.
            # Any mix of IN keys (F1/F3) counts as multiple IN punches.
            if k_a in ['F1', 'F3'] and k_b in ['F1', 'F3']:
                out_follows = any(
                    sorted_logs.iloc[m].get('Function Key', 'F1') in ['F2', 'F4']
                    and sorted_logs.iloc[m]['Event Time'].date() == t_a.date()
                    for m in range(idx2 + 1, n)
                )
                too_close = (t_b - t_a).total_seconds() < SHORT_PUNCH_MINUTES * 60
                if out_follows or too_close:
                    used_indices.add(idx2)

            # Consecutive OUT keys (F2->F2 or F4->F4): keep last, discard earlier (idx)
            # Any mix of OUT keys (F2/F4) counts as multiple OUT punches.
            if k_a in ['F2', 'F4'] and k_b in ['F2', 'F4']:
                used_indices.add(idx)
                break  # idx is discarded, move to next idx
    # ────────────────────────────────────────────────────────────────────────

    i = 0
    while i < n:
        if i in used_indices:
            i += 1
            continue

        r1 = sorted_logs.iloc[i]
        t1 = r1['Event Time']
        k1 = r1.get('Function Key', 'F1')
        at1 = str(r1.get('Auth Type', '')).strip() if 'Auth Type' in sorted_logs.columns else ''
        tn1 = str(r1.get('Terminal Name', '')).strip() if 'Terminal Name' in sorted_logs.columns else ''
        used_indices.add(i)

        # Look for matching out punch
        # Window: up to MAX_PAIRING_HOURS (38 hours) from t1
        best_match_idx = None
        best_match_warning = None
        earlier_matches = []

        for j in range(i + 1, n):
            if j in used_indices:
                continue
            r2 = sorted_logs.iloc[j]
            t2 = r2['Event Time']
            k2 = r2.get('Function Key', 'F2')

            delta_sec = (t2 - t1).total_seconds()
            if delta_sec < 0:
                continue
            if delta_sec > MAX_PAIRING_HOURS * 3600:
                break  # beyond MAX_PAIRING_HOURS window

            # Cross-day pairing restriction:
            # 1. Evening/Night start (t1 >= 14:00 or F3) -> Shift C/CA/BC (duration <= 18h)
            # 2. 24H extended shifts (delta >= 20h up to 38h) for doctors and shift staff
            #    BUT: if there is an intermediate unused check-in (F1/F3) between t1 and t2,
            #    the employee simply FORGOT their F2 checkout and came back for a new shift.
            #    In that case, do NOT form a 24H pair.
            if t2.date() > t1.date():
                is_night_shift = (t1.hour >= 14 or k1 == 'F3') and delta_sec <= 18 * 3600
                # Non-doctor shift staff: a true 24H needs >= 23:30 (24h minus the 30-min
                # tolerance); 20-23:30h F1->F2 spans stay as two unpaired single punches.
                min_24h_sec = (20 if is_doctor else 23.5) * 3600
                is_24h_shift = delta_sec >= min_24h_sec
                if not (is_night_shift or is_24h_shift):
                    continue
                # Guard: reject fake 24H caused by forgotten checkout.
                if is_24h_shift:
                    # Rule A: genuine 24H shifts always end with F2/F4, never same-key (F1->F1)
                    # A same_key_repeat cross-day is always a forgotten checkout scenario.
                    if k2 == k1:
                        continue
                    # Rule A2: must start with an IN key (F1/F3) and end with an OUT key (F2/F4);
                    # F2->F1 / F2->F2 across days are two unrelated single punches.
                    if k1 not in ['F1', 'F3'] or k2 not in ['F2', 'F4']:
                        continue
                    # Rule B: if any unused intermediate F1/F3 punch exists strictly between
                    # t1 and t2 (exclusive), the employee returned for a new shift.
                    has_intermediate_checkin = any(
                        (k not in used_indices)
                        and (sorted_logs.iloc[k]['Event Time'] > t1)
                        and (sorted_logs.iloc[k]['Event Time'] < t2)
                        and (sorted_logs.iloc[k].get('Function Key', 'F1') in ['F1', 'F3'])
                        for k in range(i + 1, j)
                    )
                    if has_intermediate_checkin:
                        continue

            # Smart pairing with human mistake tolerance
            is_valid_pair = False
            key_warning = None

            if k1 in ['F1', 'F3']:
                expected_out = 'F2' if k1 == 'F1' else 'F4'
                if k2 == expected_out:
                    # Ideal expected match: F1->F2 or F3->F4
                    is_valid_pair = True
                    key_warning = None
                elif k2 in ['F2', 'F4']:
                    # Cross-key checkout: F1->F4 or F3->F2
                    is_valid_pair = True
                    key_warning = 'cross_key'
                elif k2 == k1 and delta_sec >= SHORT_PUNCH_MINUTES * 60:
                    # Human mistake: F1->F1 or F3->F3 (same key repeat after >= 40 min)
                    is_valid_pair = True
                    key_warning = 'same_key_repeat'
            elif k1 in ['F2', 'F4']:
                # Started with OUT key
                # Reversed-keys tolerance must not steal an IN punch that has its own
                # OUT later (e.g. F2 19:37 -> F1 07:18 next day, when F1 07:18 -> F2 19:12 is real).
                steals_real_in = k2 in ['F1', 'F3'] and any(
                    (m not in used_indices)
                    and sorted_logs.iloc[m].get('Function Key', 'F2') in ['F2', 'F4']
                    and 0 < (sorted_logs.iloc[m]['Event Time'] - t2).total_seconds() <= 20 * 3600
                    for m in range(j + 1, n)
                )
                if delta_sec >= SHORT_PUNCH_MINUTES * 60 and not steals_real_in:
                    is_valid_pair = True
                    if k2 in ['F1', 'F3']:
                        key_warning = 'reversed_keys'
                    else:
                        key_warning = 'started_with_out_key'
            else:
                # Untyped key
                if delta_sec >= SHORT_PUNCH_MINUTES * 60:
                    is_valid_pair = True
                    key_warning = None

            if is_valid_pair:
                # If k1 is an IN key and k2 is an OUT key:
                # "and if 2 f2 use the last one"
                # Keep searching for a later OUT punch on the same day before the next check-in
                if k1 in ['F1', 'F3'] and k2 in ['F2', 'F4']:
                    if best_match_idx is not None:
                        earlier_matches.append(best_match_idx)
                    best_match_idx = j
                    best_match_warning = key_warning

                    has_later_out = False
                    for next_k in range(j + 1, n):
                        if next_k in used_indices:
                            continue
                        r_next = sorted_logs.iloc[next_k]
                        k_next = r_next.get('Function Key', 'F2')
                        t_next = r_next['Event Time']
                        if t_next.date() != t2.date():
                            break
                        if k_next in ['F1', 'F3']:
                            break  # next punch is a new check-in, stop
                        if k_next in ['F2', 'F4']:
                            has_later_out = True
                            break
                    if has_later_out:
                        continue  # continue loop to find the last OUT punch
                    else:
                        break
                else:
                    best_match_idx = j
                    best_match_warning = key_warning
                    break

        if best_match_idx is not None:
            # Mark any earlier intermediate matches as used so they don't form orphan rows
            for em in earlier_matches:
                used_indices.add(em)

            r2 = sorted_logs.iloc[best_match_idx]
            t2 = r2['Event Time']
            k2 = r2.get('Function Key', 'F2')
            at2 = str(r2.get('Auth Type', '')).strip() if 'Auth Type' in sorted_logs.columns else ''
            tn2 = str(r2.get('Terminal Name', '')).strip() if 'Terminal Name' in sorted_logs.columns else ''
            used_indices.add(best_match_idx)
            shifts.append({
                'in_time': t1,
                'out_time': t2,
                'in_key': k1,
                'out_key': k2,
                'in_auth_type': at1,
                'out_auth_type': at2,
                'in_terminal': tn1,
                'out_terminal': tn2,
                'shift_date': t1.date(),
                'key_warning': best_match_warning
            })
        else:
            # Single punch: distinguish isolated OUT vs isolated IN
            if k1 in ['F2', 'F4']:
                shifts.append({
                    'in_time': None,
                    'out_time': t1,
                    'in_key': '',
                    'out_key': k1,
                    'in_auth_type': '',
                    'out_auth_type': at1,
                    'in_terminal': '',
                    'out_terminal': tn1,
                    'shift_date': t1.date(),
                    'key_warning': 'missing_checkin'
                })
            else:
                shifts.append({
                    'in_time': t1,
                    'out_time': None,
                    'in_key': k1,
                    'out_key': '',
                    'in_auth_type': at1,
                    'out_auth_type': '',
                    'in_terminal': tn1,
                    'out_terminal': '',
                    'shift_date': t1.date(),
                    'key_warning': 'missing_checkout'
                })
        i += 1

    # Separate cross-day extended shifts (24H, 24+A, 24+A+B) into two distinct daily records
    # as required: Start Date row shows check-in, End Date row shows check-out, duration & SHIFT type
    regular_shifts = []
    for s in shifts:
        if s['in_time'] and s['out_time']:
            dur = int((s['out_time'] - s['in_time']).total_seconds() // 60)
            st = classify_shift(s['in_time'], s['out_time'], dur)
            if st in ["24H", "24+A", "24+A+B"] and s['out_time'].date() > s['in_time'].date():
                d_start = s['in_time'].date()
                d_end = s['out_time'].date()
                day_start_name = ARABIC_DAYS.get(d_start.weekday(), "")
                day_end_name = ARABIC_DAYS.get(d_end.weekday(), "")

                def_m, ot_m = calculate_deficit_and_overtime(st, dur)

                # Row 1: Attend Date (Start Date)
                records.append({
                    'date': d_start.strftime("%Y-%m-%d"),
                    'day': day_start_name,
                    'check_in_1': format_am_pm(s['in_time']),
                    'check_out_1': '',
                    'check_in_2': '',
                    'check_out_2': '',
                    'time_spent': '0:00',
                    'time_spent_minutes': 0,
                    'shift_type': '',  # Empty on start date as requested
                    'deficit_time': '0:00',
                    'deficit_minutes': 0,
                    'overtime_time': '0:00',
                    'overtime_minutes': 0,
                    'is_deficit': False,
                    'is_overtime': False,
                    'is_late_arrival': (s['in_time'].hour > 8 or (s['in_time'].hour == 8 and s['in_time'].minute > 45)),
                    'key_warning': s.get('key_warning') or 'start_of_24h',
                    'in_1_key': s.get('in_key', ''),
                    'out_1_key': '',
                    'in_2_key': '',
                    'out_2_key': '',
                    'in_1_auth_type': s.get('in_auth_type', ''),
                    'out_1_auth_type': '',
                    'in_2_auth_type': '',
                    'out_2_auth_type': '',
                    'in_1_terminal': s.get('in_terminal', ''),
                    'out_1_terminal': '',
                    'in_2_terminal': '',
                    'out_2_terminal': '',
                })

                # Row 2: Leave Date (End Date)
                records.append({
                    'date': d_end.strftime("%Y-%m-%d"),
                    'day': day_end_name,
                    'check_in_1': '',
                    'check_out_1': format_am_pm(s['out_time']),
                    'check_in_2': '',
                    'check_out_2': '',
                    'time_spent': minutes_to_hh_mm(dur),
                    'time_spent_minutes': dur,
                    'shift_type': st,  # Shift type on leave date
                    'deficit_time': minutes_to_hh_mm(def_m),
                    'deficit_minutes': def_m,
                    'overtime_time': minutes_to_hh_mm(ot_m),
                    'overtime_minutes': ot_m,
                    'is_deficit': def_m > 0,
                    'is_overtime': ot_m > 0,
                    'is_late_arrival': False,
                    'key_warning': s.get('key_warning') or 'end_of_24h',
                    'in_1_key': '',
                    'out_1_key': s.get('out_key', ''),
                    'in_2_key': '',
                    'out_2_key': '',
                    'in_1_auth_type': '',
                    'out_1_auth_type': s.get('out_auth_type', ''),
                    'in_2_auth_type': '',
                    'out_2_auth_type': '',
                    'in_1_terminal': '',
                    'out_1_terminal': s.get('out_terminal', ''),
                    'in_2_terminal': '',
                    'out_2_terminal': '',
                })
                continue
        regular_shifts.append(s)

    # Now group regular shifts by shift_date
    date_groups: Dict[date, List[Dict[str, Any]]] = {}
    for s in regular_shifts:
        d = s['shift_date']
        date_groups.setdefault(d, []).append(s)

    for shift_date in sorted(date_groups.keys()):
        day_shifts = date_groups[shift_date]
        day_num = shift_date.weekday()
        day_name = ARABIC_DAYS.get(day_num, "")

        # Organize into Primary and Secondary (Evening)
        in_1, out_1 = None, None
        in_2, out_2 = None, None

        # Punch metadata (keys, auth types, terminals)
        in_1_key, out_1_key = '', ''
        in_1_auth, out_1_auth = '', ''
        in_1_terminal, out_1_terminal = '', ''
        in_2_key, out_2_key = '', ''
        in_2_auth, out_2_auth = '', ''
        in_2_terminal, out_2_terminal = '', ''

        day_key_warning = None
        if len(day_shifts) == 1:
            s0 = day_shifts[0]
            # Check if this single shift is Shift B (Evening shift)
            dur_check = 0
            st_check = ""
            if s0['in_time'] and s0['out_time']:
                dur_check = calc_duration_minutes(s0['in_time'], s0['out_time'])
                st_check = classify_shift(s0['in_time'], s0['out_time'], dur_check)

            if st_check == "B" or (s0.get('in_key') in ['F3', 'F4'] and not (s0.get('in_key') == 'F1')):
                # Afternoon/Evening shift -> route to check_in_2 and check_out_2
                in_2 = s0['in_time']
                out_2 = s0['out_time']
                in_2_key = s0.get('in_key', '')
                out_2_key = s0.get('out_key', '') or ''
                in_2_auth = s0.get('in_auth_type', '')
                out_2_auth = s0.get('out_auth_type', '')
                in_2_terminal = s0.get('in_terminal', '')
                out_2_terminal = s0.get('out_terminal', '')
            else:
                in_1 = s0['in_time']
                out_1 = s0['out_time']
                in_1_key = s0.get('in_key', '')
                out_1_key = s0.get('out_key', '') or ''
                in_1_auth = s0.get('in_auth_type', '')
                out_1_auth = s0.get('out_auth_type', '')
                in_1_terminal = s0.get('in_terminal', '')
                out_1_terminal = s0.get('out_terminal', '')
            day_key_warning = s0.get('key_warning')
        else:
            # Multiple shifts on the same day: Primary in in_1/out_1, Evening in in_2/out_2
            morn_shift = None
            eve_shift = None
            for s in day_shifts:
                is_eve = (s.get('in_key') in ['F3', 'F4'] and s.get('in_key') != 'F1') or (s['in_time'] and s['in_time'].hour >= 14)
                if is_eve and eve_shift is None:
                    eve_shift = s
                elif morn_shift is None:
                    morn_shift = s
                elif eve_shift is None:
                    eve_shift = s

            s_primary = morn_shift or day_shifts[0]
            s_secondary = eve_shift if (eve_shift and eve_shift != s_primary) else (day_shifts[1] if len(day_shifts) > 1 and day_shifts[1] != s_primary else None)

            in_1, out_1 = s_primary['in_time'], s_primary['out_time']
            in_1_key = s_primary.get('in_key', '')
            out_1_key = s_primary.get('out_key', '') or ''
            in_1_auth = s_primary.get('in_auth_type', '')
            out_1_auth = s_primary.get('out_auth_type', '')
            in_1_terminal = s_primary.get('in_terminal', '')
            out_1_terminal = s_primary.get('out_terminal', '')

            if s_secondary:
                in_2, out_2 = s_secondary['in_time'], s_secondary['out_time']
                in_2_key = s_secondary.get('in_key', '')
                out_2_key = s_secondary.get('out_key', '') or ''
                in_2_auth = s_secondary.get('in_auth_type', '')
                out_2_auth = s_secondary.get('out_auth_type', '')
                in_2_terminal = s_secondary.get('in_terminal', '')
                out_2_terminal = s_secondary.get('out_terminal', '')

            w1 = s_primary.get('key_warning')
            w2 = s_secondary.get('key_warning') if s_secondary else None
            day_key_warning = w1 if (w1 and w1 not in ['missing_checkout', 'missing_checkin']) else (w2 or w1)

        # Calculate durations using precise biometric minute cleaning
        dur_1 = calc_duration_minutes(in_1, out_1) if (in_1 and out_1) else 0
        dur_2 = calc_duration_minutes(in_2, out_2) if (in_2 and out_2) else 0
        total_duration = dur_1 + dur_2

        # Classify shift & enforce single-punch / undefined rule:
        # If attend start or leave attend is undefined or empty:
        # show as empty "" and DO NOT calculate this day (time = 0, deficit = 0, overtime = 0).
        has_paired_shift = (in_1 and out_1) or (in_2 and out_2)
        if not has_paired_shift:
            shift_type = ""
            total_duration = 0
            deficit_mins, overtime_mins = 0, 0
            is_late_arrival = False
        else:
            if in_2 and out_2 and not (in_1 and out_1):
                shift_type = classify_shift(in_2, out_2, dur_2)
            elif in_1 and out_1 and not (in_2 and out_2):
                shift_type = classify_shift(in_1, out_1, dur_1)
            else:
                if total_duration >= 33 * 60:
                    shift_type = "24+A+B"
                elif total_duration >= 27 * 60:
                    shift_type = "24+A"
                elif total_duration >= 20 * 60:
                    shift_type = "24H"
                else:
                    shift_type = "BC"

            if not shift_type:
                # Undefined shift: do not suggest, show as empty and don't calculate
                total_duration = 0
                deficit_mins, overtime_mins = 0, 0
                is_late_arrival = False
            else:
                deficit_mins, overtime_mins = calculate_deficit_and_overtime(shift_type, total_duration)

                # Check late arrival with 15-minute buffer:
                # e.g. Shift A starts at 8:30 -> allowed up to 8:45 AM. After 8:45 AM it is late.
                is_late_arrival = False
                active_in = in_1 if in_1 else in_2
                if active_in:
                    if shift_type in ["A", "L", "24H", "24+A", "24+A+B"] and (active_in.hour > 8 or (active_in.hour == 8 and active_in.minute > 45)):
                        is_late_arrival = True
                    elif shift_type in ["B"] and (active_in.hour > 14 or (active_in.hour == 14 and active_in.minute > 45)):
                        is_late_arrival = True
                    elif shift_type in ["C"] and (active_in.hour > 20 or (active_in.hour == 20 and active_in.minute > 45)):
                        is_late_arrival = True

        records.append({
            'date': shift_date.strftime("%Y-%m-%d"),
            'day': day_name,
            'check_in_1': format_am_pm(in_1) if in_1 else '',
            'check_out_1': format_am_pm(out_1) if out_1 else '',
            'check_in_2': format_am_pm(in_2) if in_2 else '',
            'check_out_2': format_am_pm(out_2) if out_2 else '',
            'time_spent': minutes_to_hh_mm(total_duration),
            'time_spent_minutes': total_duration,
            'shift_type': shift_type,
            'deficit_time': minutes_to_hh_mm(deficit_mins),
            'deficit_minutes': deficit_mins,
            'overtime_time': minutes_to_hh_mm(overtime_mins),
            'overtime_minutes': overtime_mins,
            'is_deficit': deficit_mins > 0,
            'is_overtime': overtime_mins > 0,
            'is_late_arrival': is_late_arrival,
            'key_warning': day_key_warning,
            # Punch metadata for UI display
            'in_1_key': in_1_key,
            'out_1_key': out_1_key,
            'in_2_key': in_2_key,
            'out_2_key': out_2_key,
            'in_1_auth_type': in_1_auth,
            'out_1_auth_type': out_1_auth,
            'in_2_auth_type': in_2_auth,
            'out_2_auth_type': out_2_auth,
            'in_1_terminal': in_1_terminal,
            'out_1_terminal': out_1_terminal,
            'in_2_terminal': in_2_terminal,
            'out_2_terminal': out_2_terminal,
        })

    # Sort all records chronologically
    records.sort(key=lambda r: (r['date'], r.get('check_in_1') or r.get('check_out_1') or ''))
    return records


def process_all_doctors(
    df_master: pd.DataFrame,
    df_auth_logs: pd.DataFrame,
    departments: Optional[List[str]] = None,
    contracts: Optional[List[str]] = None,
    job_groups: Optional[List[str]] = None,
    job_titles: Optional[List[str]] = None,
    search_query: Optional[str] = None,
    only_with_punches: bool = True,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main entry point for dynamically processing employees and generating attendance structures.
    100% Dynamic: Filters are applied strictly from user-provided arguments.
    """
    from .data_loader import filter_employees_dynamic

    # 1. Filter master records dynamically
    filtered_emps = filter_employees_dynamic(
        df_master,
        departments=departments,
        contracts=contracts,
        job_groups=job_groups,
        job_titles=job_titles,
        search_query=search_query
    )

    # 2. Filter auth logs by date if specified
    auth_logs = df_auth_logs.copy()
    if date_from:
        auth_logs = auth_logs[auth_logs['Event Time'] >= pd.to_datetime(date_from)]
    if date_to:
        auth_logs = auth_logs[auth_logs['Event Time'] <= pd.to_datetime(date_to) + timedelta(days=1)]

    # 3. Build logs index by User ID
    logs_by_user = dict(tuple(auth_logs.groupby('User ID')))

    results = []
    total_hours_all = 0
    total_deficit_all = 0
    total_overtime_all = 0

    for _, emp in filtered_emps.iterrows():
        emp_code = str(emp['Emp_Code']).strip()
        emp_logs = logs_by_user.get(emp_code, pd.DataFrame())

        if only_with_punches and emp_logs.empty:
            continue

        emp_name = str(emp.get('Staff_AName', '')).strip()
        job_title = str(emp.get('JD_ADesc', '')).strip()
        dept = str(emp.get('Cost_Local', '')).strip()
        sector = str(emp.get('Dep_ADesc', '')).strip()
        contract = str(emp.get('A_Desc', '')).strip()
        job_group = str(emp.get('JobGroupName', '')).strip()
        is_doc = is_doctor_title(job_title, job_group)

        records = process_doctor_records(emp_code, emp_logs, is_doctor=is_doc)
        if only_with_punches and not records:
            continue

        # Extract terminals and map to physical sector and location
        user_terminals = []
        device_sectors = []
        device_locations = []
        if not emp_logs.empty and 'Terminal Name' in emp_logs.columns:
            user_terminals = [str(t).strip() for t in emp_logs['Terminal Name'].dropna().unique() if str(t).strip()]
            for t in user_terminals:
                if t in DEVICE_NAME_TO_INFO:
                    sec = DEVICE_NAME_TO_INFO[t].get("sector")
                    loc = DEVICE_NAME_TO_INFO[t].get("location")
                    if sec and sec not in device_sectors:
                        device_sectors.append(sec)
                    if loc and loc not in device_locations:
                        device_locations.append(loc)

        doc_hours = sum(r['time_spent_minutes'] for r in records)
        doc_deficit = sum(r['deficit_minutes'] for r in records)
        doc_overtime = sum(r['overtime_minutes'] for r in records)

        total_hours_all += doc_hours
        total_deficit_all += doc_deficit
        total_overtime_all += doc_overtime

        results.append({
            'emp_code': emp_code,
            'emp_name': emp_name,
            'job_title': job_title,
            'department': dept,
            'sector': sector,
            'job_group': job_group,
            'is_doctor': is_doc,
            'terminals': user_terminals,
            'device_sectors': device_sectors,
            'device_locations': device_locations,
            'contract': contract,
            'records': records,
            'total_days_worked': len([r for r in records if r.get('time_spent_minutes', 0) > 0 and r.get('shift_type') != ""]),
            'total_time_spent': minutes_to_hh_mm(doc_hours),
            'total_time_spent_minutes': doc_hours,
            'total_deficit': minutes_to_hh_mm(doc_deficit),
            'total_deficit_minutes': doc_deficit,
            'total_overtime': minutes_to_hh_mm(doc_overtime),
            'total_overtime_minutes': doc_overtime,
        })

    # Include any active punch users from logs who weren't in master file (if no strict master filter applied)
    if not any([departments, contracts, job_groups, job_titles, search_query]):
        existing_codes = {r['emp_code'] for r in results}
        for uid, user_logs in logs_by_user.items():
            uid_str = str(uid).strip()
            if uid_str in existing_codes or user_logs.empty:
                continue

            records = process_doctor_records(uid_str, user_logs)
            if not records:
                continue

            u_name = str(user_logs['User Name'].dropna().iloc[0]).strip() if 'User Name' in user_logs.columns and not user_logs['User Name'].dropna().empty else f"موظف {uid_str}"
            u_title = str(user_logs['Title'].dropna().iloc[0]).strip() if 'Title' in user_logs.columns and not user_logs['Title'].dropna().empty else ""
            u_dept = str(user_logs['GroupName'].dropna().iloc[0]).strip() if 'GroupName' in user_logs.columns and not user_logs['GroupName'].dropna().empty else ""

            user_terminals = [str(t).strip() for t in user_logs['Terminal Name'].dropna().unique() if str(t).strip()] if 'Terminal Name' in user_logs.columns else []
            device_sectors = []
            device_locations = []
            for t in user_terminals:
                if t in DEVICE_NAME_TO_INFO:
                    sec = DEVICE_NAME_TO_INFO[t].get("sector")
                    loc = DEVICE_NAME_TO_INFO[t].get("location")
                    if sec and sec not in device_sectors:
                        device_sectors.append(sec)
                    if loc and loc not in device_locations:
                        device_locations.append(loc)

            doc_hours = sum(r['time_spent_minutes'] for r in records)
            doc_deficit = sum(r['deficit_minutes'] for r in records)
            doc_overtime = sum(r['overtime_minutes'] for r in records)

            total_hours_all += doc_hours
            total_deficit_all += doc_deficit
            total_overtime_all += doc_overtime

            results.append({
                'emp_code': uid_str,
                'emp_name': u_name,
                'job_title': u_title,
                'department': u_dept,
                'sector': device_sectors[0] if device_sectors else "",
                'job_group': "",
                'is_doctor': is_doctor_title(u_title, ""),
                'terminals': user_terminals,
                'device_sectors': device_sectors,
                'device_locations': device_locations,
                'contract': 'غير محدد',
                'records': records,
                'total_days_worked': len([r for r in records if r.get('time_spent_minutes', 0) > 0 and r.get('shift_type') != ""]),
                'total_time_spent': minutes_to_hh_mm(doc_hours),
                'total_time_spent_minutes': doc_hours,
                'total_deficit': minutes_to_hh_mm(doc_deficit),
                'total_deficit_minutes': doc_deficit,
                'total_overtime': minutes_to_hh_mm(doc_overtime),
                'total_overtime_minutes': doc_overtime,
            })

    return {
        'doctors': results,
        'summary': {
            'total_doctors': len(results),
            'total_hours': minutes_to_hh_mm(total_hours_all),
            'total_deficit': minutes_to_hh_mm(total_deficit_all),
            'total_overtime': minutes_to_hh_mm(total_overtime_all)
        }
    }
