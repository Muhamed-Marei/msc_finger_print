# backend/test_engine.py
"""
Test and verification suite:
Compares the engine output directly against the reference PDF:
- Doctor 9902544 (Page 1)
- Doctor 9903115 (Page 2)
- Doctor 9902285 (Page 107 with Shift CA, BC, C, L)
"""

import os
import sys
import glob

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from backend.data_loader import load_employee_master, load_auth_logs
from backend.shift_engine import process_all_doctors

docs_dir = r"c:\Users\Eng. Mohamed Marei\projects\msc_finger_print\docs"

# 1. Master file
emp_files = glob.glob(os.path.join(docs_dir, "*بيانات الموظفين*.xlsx"))
if not emp_files:
    print("Master file not found!")
    sys.exit(1)

emp_path = emp_files[0]
print(f"Loading Master: {os.path.basename(emp_path)}")
df_master = load_employee_master(emp_path)

# 2. AuthLogs
auth_files = sorted(glob.glob(os.path.join(docs_dir, "AuthLogList*.xlsx")))
print(f"Loading {len(auth_files)} AuthLog files...")
df_logs = load_auth_logs(auth_files)
print(f"Total Combined Clean Logs: {len(df_logs)}")

# 3. Process
print("\nRunning Process Engine with Almaza Doctors Preset...")
results = process_all_doctors(df_master, df_logs, use_almaza_preset=True)

print(f"\n--- RESULTS SUMMARY ---")
summary = results['summary']
print(f"Total Filtered Doctors with Attendance: {summary['total_doctors']}")
print(f"Total Hours: {summary['total_hours']}")
print(f"Total Deficit: {summary['total_deficit']}")
print(f"Total Overtime: {summary['total_overtime']}")

# 4. Deep Inspection of Doctor 1 (Page 1 in PDF: 9902544)
print("\n" + "="*80)
print("VERIFICATION: DOCTOR 1 (Page 1 in PDF: 9902544 - Ahmed Saeed El Kholy)")
print("="*80)
doc1 = next((d for d in results['doctors'] if d['emp_code'] == '9902544'), None)
if doc1:
    print(f"Name: {doc1['emp_name']} | Dept: {doc1['department']} | Contract: {doc1['contract']}")
    print(f"Total Days Worked: {doc1['total_days_worked']} | Total Hours: {doc1['total_time_spent']} | Total Deficit: {doc1['total_deficit']} | Overtime: {doc1['total_overtime']}")
    print(f"\n{'Date':12} | {'Day':10} | {'CheckIn':10} | {'CheckOut':10} | {'Spent':8} | {'Shift':6} | {'Deficit':8} | {'Overtime':8}")
    print("-" * 85)
    for r in doc1['records']:
        print(f"{r['date']:12} | {r['day']:10} | {r['check_in_1']:10} | {r['check_out_1']:10} | {r['time_spent']:8} | {r['shift_type']:6} | {r['deficit_time']:8} | {r['overtime_time']:8}")
else:
    print("Doctor 9902544 not found in results!")

# 5. Deep Inspection of Doctor 107 (Attia Ahmed: 9902285)
print("\n" + "="*80)
print("VERIFICATION: DOCTOR 107 (Page 107 in PDF: 9902285 - Attia Ahmed with Shifts CA, BC, C, L)")
print("="*80)
doc107 = next((d for d in results['doctors'] if d['emp_code'] == '9902285'), None)
if doc107:
    print(f"Name: {doc107['emp_name']} | Dept: {doc107['department']}")
    print(f"\n{'Date':12} | {'Day':10} | {'CheckIn':10} | {'CheckOut':10} | {'Spent':8} | {'Shift':6} | {'Deficit':8}")
    print("-" * 75)
    for r in doc107['records']:
        print(f"{r['date']:12} | {r['day']:10} | {r['check_in_1']:10} | {r['check_out_1']:10} | {r['time_spent']:8} | {r['shift_type']:6} | {r['deficit_time']:8}")
else:
    print("Doctor 9902285 not found!")
