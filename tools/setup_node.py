import os
import sys
import urllib.request
import zipfile
import shutil

NODE_VERSION = "v20.18.0"
ZIP_URL = f"https://nodejs.org/dist/{NODE_VERSION}/node-{NODE_VERSION}-win-x64.zip"
TARGET_DIR = os.path.abspath("tools/node")

if os.path.exists(os.path.join(TARGET_DIR, "node.exe")):
    print("Node.js is already installed at:", TARGET_DIR)
    sys.exit(0)

os.makedirs("tools", exist_ok=True)
zip_path = os.path.abspath("tools/node.zip")

print(f"Downloading Node.js {NODE_VERSION} from {ZIP_URL}...")
def progress(count, block_size, total_size):
    percent = int(count * block_size * 100 / total_size)
    if count % 1000 == 0 or percent >= 100:
        print(f"Downloaded {percent}% ({count * block_size // (1024*1024)} MB)...")

urllib.request.urlretrieve(ZIP_URL, zip_path, reporthook=progress)
print("Download finished. Extracting...")

temp_extract = os.path.abspath("tools/temp_node")
os.makedirs(temp_extract, exist_ok=True)

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(temp_extract)

# Inside temp_extract is 'node-v20.18.0-win-x64'
extracted_sub = [os.path.join(temp_extract, d) for d in os.listdir(temp_extract) if os.path.isdir(os.path.join(temp_extract, d))][0]

if os.path.exists(TARGET_DIR):
    shutil.rmtree(TARGET_DIR)

shutil.move(extracted_sub, TARGET_DIR)

# Clean up
if os.path.exists(zip_path):
    os.remove(zip_path)
if os.path.exists(temp_extract):
    shutil.rmtree(temp_extract)

print("Node.js setup successfully at:", TARGET_DIR)
