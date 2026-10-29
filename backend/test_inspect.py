import sys, os, glob, json
import pandas as pd
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')
from backend.data_loader import load_auth_logs
from backend.shift_engine import process_doctor_records

docs_dir = os.path.abspath('docs')
files = sorted(glob.glob(os.path.join(docs_dir, 'AuthLogList*.xlsx')))
df = load_auth_logs(files)
emp_df = df[df['User ID'].astype(str).str.contains('10010911')].sort_values('Event Time')

records = process_doctor_records('10010911', emp_df, is_doctor=True)
for r in records:
    if '2026-10-05' <= r['date'] <= '2026-10-08':
        print(f"{r['date']} | {r['day']} | in1: {r.get('check_in_1')} | out1: {r.get('check_out_1')} | in2: {r.get('check_in_2')} | out2: {r.get('check_out_2')} | type: {r.get('shift_type')} | time: {r.get('time_spent')} | warn: {r.get('key_warning')}")
