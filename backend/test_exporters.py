# backend/test_exporters.py
"""
Verification of PDF and Excel generation.
"""

import os
import sys
import glob
import pypdf

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from backend.data_loader import load_employee_master, load_auth_logs
from backend.shift_engine import process_all_doctors
from backend.excel_generator import generate_excel_report
from backend.pdf_generator import generate_pdf_report

docs_dir = 'docs'
emp_file = glob.glob(os.path.join(docs_dir, "*بيانات الموظفين*.xlsx"))[0]
auth_files = sorted(glob.glob(os.path.join(docs_dir, "AuthLogList*.xlsx")))

print("1. Loading Master and Logs...")
df_master = load_employee_master(emp_file)
df_logs = load_auth_logs(auth_files)

print("2. Processing Doctors Attendance...")
data = process_all_doctors(df_master, df_logs, use_almaza_preset=True, only_with_punches=True)
print(f"Total processed doctors: {len(data['doctors'])}")

# Let's test on the first 10 doctors for fast verification
sample_data = {
    'doctors': data['doctors'][:10],
    'summary': data['summary']
}

out_dir = 'output'
os.makedirs(out_dir, exist_ok=True)

# 3. Test Excel Export
excel_path = os.path.join(out_dir, "test_attendance_report.xlsx")
print(f"\n3. Generating Excel Report: {excel_path}...")
generate_excel_report(sample_data, excel_path)
print(f"Excel generated successfully! Size: {os.path.getsize(excel_path):,} bytes")

# 4. Test PDF Export
pdf_path = os.path.join(out_dir, "test_attendance_report.pdf")
print(f"\n4. Generating PDF Report: {pdf_path}...")
generate_pdf_report(sample_data, pdf_path)
print(f"PDF generated successfully! Size: {os.path.getsize(pdf_path):,} bytes")

reader = pypdf.PdfReader(pdf_path)
print(f"Verified PDF Pages: {len(reader.pages)}")
print(f"Page 1 Text Sample:\n{reader.pages[0].extract_text()[:400]}")
