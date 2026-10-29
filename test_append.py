import glob
import requests

auth_files = sorted(glob.glob('data_test/*.xlsx'))
if not auth_files:
    auth_files = sorted(glob.glob('docs/AuthLogList*.xlsx'))

print("Selected file to append:", auth_files[0])
with open(auth_files[0], 'rb') as f:
    files = [
        ('auth_files', (auth_files[0], f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))
    ]
    r = requests.post('http://127.0.0.1:8000/api/batches/batch_20261024_110238/append-files', files=files)
    print("Status:", r.status_code)
    try:
        print("Response:", r.json())
    except Exception as e:
        print("Raw text:", r.text[:200])

# review the plan to enhance  ,and review the calculation way . 

# need to handel the way to show the config error like if employee in 8 AM use f1 then in 8 pm forget and use f1 (where should use f2 ) and like that if start the date with f2 and other case (  the human mistake ) .

# review the plan to enhance  ,and review the calculation way . 

# need to handel the way to show the config error like if employee in 8 AM use f1 then in 8 pm forget and use f1 (where should use f2 ) and like that if start the date with f2 and other case (  the human mistake ) .6