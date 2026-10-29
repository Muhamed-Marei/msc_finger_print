import sys, os, glob
import pandas as pd
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')
from backend.data_loader import load_auth_logs

raw_dir = 'storage/batches/batch_20261028_092512/raw'
auth_files = [os.path.join(raw_dir, f) for f in os.listdir(raw_dir) if 'AuthLog' in f]
df = load_auth_logs(auth_files)
emp_df = df[df['User ID'].astype(str).str.contains('10010911')].sort_values('Event Time')
print('Punches for 10010911 in batch raw files:')
for idx, r in emp_df.iterrows():
    if '2026-10-05' <= str(r['Event Time']) <= '2026-10-08':
        t = r['Event Time']
        k = r.get('Function Key')
        term = r.get('Terminal Name')
        print(f"{t} | {k} | {term}")
