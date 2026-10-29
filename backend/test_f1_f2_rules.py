import sys, os
import pandas as pd
from datetime import datetime

os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')

from backend.shift_engine import process_doctor_records

print("=== Test 1: 10010911 (F1@08:07, F1@08:19) ===")
df1 = pd.DataFrame([
    {'Event Time': pd.Timestamp('2026-10-06 08:07:59'), 'Function Key': 'F1'},
    {'Event Time': pd.Timestamp('2026-10-06 08:19:59'), 'Function Key': 'F1'},
    {'Event Time': pd.Timestamp('2026-10-07 08:13:32'), 'Function Key': 'F1'},
    {'Event Time': pd.Timestamp('2026-10-07 14:27:33'), 'Function Key': 'F2'},
])
for r in process_doctor_records('10010911', df1, is_doctor=True):
    print(r['date'], r['day'], f"in1={r['check_in_1']}", f"out1={r['check_out_1']}", f"in2={r['check_in_2']}", f"out2={r['check_out_2']}", f"type={r['shift_type']}", f"time={r['time_spent']}", f"warn={r['key_warning']}")

print("\n=== Test 2: Two F2 punches (F2@14:00, F2@14:30) ===")
df2 = pd.DataFrame([
    {'Event Time': pd.Timestamp('2026-10-06 08:00:00'), 'Function Key': 'F1'},
    {'Event Time': pd.Timestamp('2026-10-06 14:00:00'), 'Function Key': 'F2'},
    {'Event Time': pd.Timestamp('2026-10-06 14:30:00'), 'Function Key': 'F2'},
])
for r in process_doctor_records('TEST02', df2, is_doctor=True):
    print(r['date'], r['day'], f"in1={r['check_in_1']}", f"out1={r['check_out_1']}", f"in2={r['check_in_2']}", f"out2={r['check_out_2']}", f"type={r['shift_type']}", f"time={r['time_spent']}", f"warn={r['key_warning']}")

print("\n=== Test 3: Multiple F1 and Multiple F2 ===")
df3 = pd.DataFrame([
    {'Event Time': pd.Timestamp('2026-10-06 08:00:00'), 'Function Key': 'F1'},
    {'Event Time': pd.Timestamp('2026-10-06 08:20:00'), 'Function Key': 'F1'},
    {'Event Time': pd.Timestamp('2026-10-06 14:00:00'), 'Function Key': 'F2'},
    {'Event Time': pd.Timestamp('2026-10-06 14:30:00'), 'Function Key': 'F2'},
])
for r in process_doctor_records('TEST03', df3, is_doctor=True):
    print(r['date'], r['day'], f"in1={r['check_in_1']}", f"out1={r['check_out_1']}", f"in2={r['check_in_2']}", f"out2={r['check_out_2']}", f"type={r['shift_type']}", f"time={r['time_spent']}", f"warn={r['key_warning']}")

print("\n=== Test 4: Only two F2s ===")
df4 = pd.DataFrame([
    {'Event Time': pd.Timestamp('2026-10-06 14:00:00'), 'Function Key': 'F2'},
    {'Event Time': pd.Timestamp('2026-10-06 14:30:00'), 'Function Key': 'F2'},
])
for r in process_doctor_records('TEST04', df4, is_doctor=True):
    print(r['date'], r['day'], f"in1={r['check_in_1']}", f"out1={r['check_out_1']}", f"in2={r['check_in_2']}", f"out2={r['check_out_2']}", f"type={r['shift_type']}", f"time={r['time_spent']}", f"warn={r['key_warning']}")

print("\n=== Test 5: F2 punches 90 min apart ===")
df5 = pd.DataFrame([
    {'Event Time': pd.Timestamp('2026-10-06 08:00:00'), 'Function Key': 'F1'},
    {'Event Time': pd.Timestamp('2026-10-06 14:00:00'), 'Function Key': 'F2'},
    {'Event Time': pd.Timestamp('2026-10-06 15:30:00'), 'Function Key': 'F2'},
])
for r in process_doctor_records('TEST05', df5, is_doctor=True):
    print(r['date'], r['day'], f"in1={r['check_in_1']}", f"out1={r['check_out_1']}", f"in2={r['check_in_2']}", f"out2={r['check_out_2']}", f"type={r['shift_type']}", f"time={r['time_spent']}", f"warn={r['key_warning']}")

print("\n=== Test 6: F1 punches 90 min apart ===")
df6 = pd.DataFrame([
    {'Event Time': pd.Timestamp('2026-10-06 08:00:00'), 'Function Key': 'F1'},
    {'Event Time': pd.Timestamp('2026-10-06 09:30:00'), 'Function Key': 'F1'},
    {'Event Time': pd.Timestamp('2026-10-06 14:30:00'), 'Function Key': 'F2'},
])
for r in process_doctor_records('TEST06', df6, is_doctor=True):
    print(r['date'], r['day'], f"in1={r['check_in_1']}", f"out1={r['check_out_1']}", f"in2={r['check_in_2']}", f"out2={r['check_out_2']}", f"type={r['shift_type']}", f"time={r['time_spent']}", f"warn={r['key_warning']}")

print("\n=== Test 7: Morning and Evening on same day ===")
df7 = pd.DataFrame([
    {'Event Time': pd.Timestamp('2026-10-06 08:00:00'), 'Function Key': 'F1'},
    {'Event Time': pd.Timestamp('2026-10-06 14:00:00'), 'Function Key': 'F2'},
    {'Event Time': pd.Timestamp('2026-10-06 14:30:00'), 'Function Key': 'F3'},
    {'Event Time': pd.Timestamp('2026-10-06 20:30:00'), 'Function Key': 'F4'},
])
for r in process_doctor_records('TEST07', df7, is_doctor=True):
    print(r['date'], r['day'], f"in1={r['check_in_1']}", f"out1={r['check_out_1']}", f"in2={r['check_in_2']}", f"out2={r['check_out_2']}", f"type={r['shift_type']}", f"time={r['time_spent']}", f"warn={r['key_warning']}")

print("\n=== Test 8: 24H shift (Friday 08:18 to Saturday 09:14) ===")
df8 = pd.DataFrame([
    {'Event Time': pd.Timestamp('2026-10-02 08:18:00'), 'Function Key': 'F1'},
    {'Event Time': pd.Timestamp('2026-10-03 09:14:00'), 'Function Key': 'F2'},
])
for r in process_doctor_records('DOC24H', df8, is_doctor=True):
    print(r['date'], r['day'], f"in1={r['check_in_1']}", f"out1={r['check_out_1']}", f"in2={r['check_in_2']}", f"out2={r['check_out_2']}", f"type={r['shift_type']}", f"time={r['time_spent']}", f"warn={r['key_warning']}")

print("\n=== Test 9: 24+A shift (Friday 09:25 to Saturday 14:16) ===")
df9 = pd.DataFrame([
    {'Event Time': pd.Timestamp('2026-10-16 09:25:00'), 'Function Key': 'F1'},
    {'Event Time': pd.Timestamp('2026-10-17 14:16:00'), 'Function Key': 'F2'},
])
for r in process_doctor_records('DOC24A', df9, is_doctor=True):
    print(r['date'], r['day'], f"in1={r['check_in_1']}", f"out1={r['check_out_1']}", f"in2={r['check_in_2']}", f"out2={r['check_out_2']}", f"type={r['shift_type']}", f"time={r['time_spent']}", f"warn={r['key_warning']}")
