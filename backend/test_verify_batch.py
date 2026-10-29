import sys, os, json
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')
from backend.batch_manager import get_batch_processed_data

batch_data = get_batch_processed_data('batch_20261028_092512')
doc = next((d for d in batch_data['doctors'] if '10010911' in d['emp_code']), None)
if doc:
    print('Doctor:', doc['emp_name'], doc['emp_code'])
    for r in doc['records']:
        if '2026-10-05' <= r['date'] <= '2026-10-08':
            d = r['date']
            day = r['day']
            in1 = r.get('check_in_1', '')
            out1 = r.get('check_out_1', '')
            in2 = r.get('check_in_2', '')
            out2 = r.get('check_out_2', '')
            st = r.get('shift_type', '')
            t = r.get('time_spent', '')
            w = r.get('key_warning', '')
            print(f"{d} | {day} | in1: {in1} | out1: {out1} | in2: {in2} | out2: {out2} | type: {st} | time: {t} | warn: {w}")
