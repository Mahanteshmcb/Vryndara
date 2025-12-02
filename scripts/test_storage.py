import sys
import os
import time

# Fix path to import SDK
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sdk.python.vryndara.storage import StorageManager

def run_test():
    # 1. Create a dummy "Movie" file (just random bytes)
    filename = "scene_01_render.mp4"
    with open(filename, "wb") as f:
        f.write(os.urandom(1024 * 1024)) # 1MB of random data
    print(f"✅ Created dummy video file: {filename}")

    # 2. Upload it to MinIO
    storage = StorageManager(bucket_name="historabook-output")
    url = storage.upload_file(filename)

    if url:
        print(f"🚀 File is safely stored at: {url}")
        print("   (This URL can now be passed to the Blender Agent)")

    # 3. Clean up local file
    os.remove(filename)

if __name__ == "__main__":
    run_test()