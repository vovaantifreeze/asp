import os
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Thread, Lock
import time
from flask import Flask

# --- Telegram ---
TG_TOKEN = os.getenv("TG_TOKEN")
CHAT_ID = os.getenv("TG_CHAT")

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": CHAT_ID, "text": message}, timeout=10)
    except Exception as e:
        print("Telegram error:", e)

# --- ASP tokens ---
TOKEN1 = os.getenv("ASP_TOKEN1")
TOKEN2 = os.getenv("ASP_TOKEN2")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://eservicii.gov.md/"
}
MAX_RETRIES = 5
RETRY_DELAY = 1.0
MAX_WORKERS = 3
print_lock = Lock()
session = requests.Session()

# --- Zile active ---
active_dates = [
   datetime(2026, 8, 11), datetime(2026, 8, 12), datetime(2026, 8, 13),
   datetime(2026, 8, 14), datetime(2026, 8, 24), datetime(2026, 8, 25),
   datetime(2026, 8, 26), datetime(2026, 8, 27), datetime(2026, 8, 28),
   datetime(2026, 9, 11)  # <-- Added 11 September
]

# --- Date check ---
def check_date(date):
    date_str = date.strftime("%Y-%m-%d")
    url = f"https://eservicii.gov.md/asp/dimtcca/api/qmatic/times/{TOKEN1}/{TOKEN2}/{date_str}"
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = session.get(url, headers=headers, timeout=5)
            
            # 1. Check HTTP status
            if r.status_code != 200:
                with print_lock:
                    print(f"[{date_str}] Attempt {attempt}: HTTP {r.status_code}")
                time.sleep(RETRY_DELAY)
                continue
            
            # 2. Check for empty body
            if not r.text or not r.text.strip():
                with print_lock:
                    print(f"[{date_str}] Attempt {attempt}: Empty response body received")
                time.sleep(RETRY_DELAY)
                continue

            # 3. Parse JSON safely
            try:
                data = r.json()
                if data:
                    return (date_str, data)
            except Exception as json_err:
                with print_lock:
                    snippet = r.text[:150].replace('\n', ' ')
                    print(f"[{date_str}] JSON Parse Fail on HTTP 200. Snippet: {snippet}")

        except Exception as e:
            with print_lock:
                print(f"Error {date_str} (Attempt {attempt}): {e}")
        
        time.sleep(RETRY_DELAY)
    return None

def run_check_loop():
    while True:
        print("Checking...", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(check_date, d) for d in active_dates]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    date_str, data = result
                    message = f"SLOT GASIT: {date_str}\n{data}"
                    print(message)
                    send_telegram(message)
        print("Nimic disponibil\n")
        time.sleep(5)

# --- Telegram heartbeat la 12h ---
def heartbeat_loop():
    while True:
        send_telegram("Botul rulează ✔")
        time.sleep(40800)

# --- Flask server ---
app = Flask("ASPChecker")

@app.route("/")
def home():
    return "ASP Checker rulează 24/7 ✅"

# --- Pornire threaduri ---
Thread(target=run_check_loop, daemon=True).start()
Thread(target=heartbeat_loop, daemon=True).start()

# --- Start Flask ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
   datetime(2026, 8, 14), datetime(2026, 8, 24), datetime(2026, 8, 25),
   datetime(2026, 8, 26), datetime(2026, 8, 27), datetime(2026, 8, 28)
]

# --- Date check ---
def check_date(date):
    date_str = date.strftime("%Y-%m-%d")
    url = f"https://eservicii.gov.md/asp/dimtcca/api/qmatic/times/{TOKEN1}/{TOKEN2}/{date_str}"
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = session.get(url, headers=headers, timeout=5)
            
            # Check for HTTP errors (e.g., 403 Cloudflare, 404, 500)
            if r.status_code != 200:
                with print_lock:
                    print(f"[{date_str}] Attempt {attempt}: HTTP Status {r.status_code}")
                time.sleep(RETRY_DELAY)
                continue
                
            # Safely parse JSON response
            try:
                data = r.json()
            except ValueError:
                with print_lock:
                    print(f"[{date_str}] Attempt {attempt}: Non-JSON response returned (likely HTML or empty)")
                time.sleep(RETRY_DELAY)
                continue

            if data:
                return (date_str, data)
                
        except Exception as e:
            with print_lock:
                print(f"Error {date_str} (Attempt {attempt}): {e}")
        
        time.sleep(RETRY_DELAY)
    return None

def run_check_loop():
    while True:
        print("Checking...", datetime.now())
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(check_date, d) for d in active_dates]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    date_str, data = result
                    message = f"SLOT GASIT: {date_str}\n{data}"
                    print(message)
                    send_telegram(message)
        print("Nimic disponibil\n")
        time.sleep(5)

# --- Telegram heartbeat la 12h ---
def heartbeat_loop():
    while True:
        send_telegram("Botul rulează ✔")
        time.sleep(40800)

# --- Flask server ---
app = Flask("ASPChecker")

@app.route("/")
def home():
    return "ASP Checker rulează 24/7 ✅"

# --- Pornire threaduri ---
Thread(target=run_check_loop, daemon=True).start()
Thread(target=heartbeat_loop, daemon=True).start()

# --- Start Flask ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
