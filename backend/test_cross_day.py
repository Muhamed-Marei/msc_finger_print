import sys, os
import pandas as pd
from datetime import datetime

os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')

from backend.test_f1_f2_rules import test_new_pairing

print("\n=== Test 8: 24H shift (Friday 08:18 to Saturday 09:14) ===")
df8 = pd.DataFrame([
    {'Event Time': pd.Timestamp('2026-10-02 08:18:00'), 'Function Key': 'F1'},
    {'Event Time': pd.Timestamp('2026-10-03 09:14:00'), 'Function Key': 'F2'},
])
for r in test_new_pairing('DOC24H', df8, is_doctor=True):
    print(r['date'], r['day'], f"in1={r['check_in_1']}", f"out1={r['check_out_1']}", f"in2={r['check_in_2']}", f"out2={r['check_out_2']}", f"type={r['shift_type']}", f"time={r['time_spent']}", f"warn={r['key_warning']}")

print("\n=== Test 9: 24+A shift (Friday 09:25 to Saturday 14:16) ===")
df9 = pd.DataFrame([
    {'Event Time': pd.Timestamp('2026-10-16 09:25:00'), 'Function Key': 'F1'},
    {'Event Time': pd.Timestamp('2026-10-17 14:16:00'), 'Function Key': 'F2'},
])
for r in test_new_pairing('DOC24A', df9, is_doctor=True):
    print(r['date'], r['day'], f"in1={r['check_in_1']}", f"out1={r['check_out_1']}", f"in2={r['check_in_2']}", f"out2={r['check_out_2']}", f"type={r['shift_type']}", f"time={r['time_spent']}", f"warn={r['key_warning']}")
