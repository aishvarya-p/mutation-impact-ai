"""
Capture Real Application Screenshots
Mutation Impact AI
"""

import os
import sys
import time
import subprocess
import threading
import urllib.request
import uvicorn

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.main import app

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
SCREENSHOT_DIR = os.path.join(PROJECT_ROOT, "docs", "screenshots")

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")

def wait_for_server(timeout=15):
    start = time.time()
    while time.time() - start < timeout:
        try:
            res = urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=1)
            if res.status == 200:
                return True
        except Exception:
            time.sleep(0.5)
    return False

def capture_screenshot(url, output_path):
    cmd = [
        CHROME_PATH,
        "--headless=new",
        "--disable-gpu",
        "--window-size=1400,900",
        f"--screenshot={output_path}",
        url
    ]
    subprocess.run(cmd, check=True)
    print(f"[+] Screenshot captured: {output_path}")

def main():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    print("[*] Starting backend server...")
    if not wait_for_server():
        print("[!] Server failed to start.")
        sys.exit(1)
        
    print("[+] Server online at http://127.0.0.1:8000")
    time.sleep(1)
    
    # 1. Dashboard screenshot
    capture_screenshot("http://127.0.0.1:8000/app#dashboard", os.path.join(SCREENSHOT_DIR, "dashboard_view.png"))
    
    # 2. Prediction console screenshot
    capture_screenshot("http://127.0.0.1:8000/app#predict", os.path.join(SCREENSHOT_DIR, "predict_view.png"))

    # 3. Model performance screenshot
    capture_screenshot("http://127.0.0.1:8000/app#performance", os.path.join(SCREENSHOT_DIR, "performance_view.png"))

    # 4. Dataset info screenshot
    capture_screenshot("http://127.0.0.1:8000/app#dataset", os.path.join(SCREENSHOT_DIR, "dataset_view.png"))
    
    print("[+] All screenshots captured successfully!")

if __name__ == "__main__":
    main()
