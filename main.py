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

headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
MAX_RETRIES = 10
RETRY_DELAY = 0.1
MAX_WORKERS = 20
print_lock = Lock()
session = requests.Session()

# --- Zile active Aprilie ---
active_dates = [
   datetime(2026,5,20),datetime(2026,4,9),datetime(2026,4,10),datetime(2026,4,13),datetime(2026,4,14),datetime(2026,4,15),datetime(2026,4,16),datetime(2026,4,17),datetime(2026,4,20),datetime(2026,4,21),datetime(2026,4,22),datetime(2026,4,23),datetime(2026,4,24)
]

# --- Checker ASP ---
def check_date(date):
    date_str = date.strftime("%Y-%m-%d")
    url = f"https://eservicii.gov.md/asp/dimtcca/api/qmatic/times/{TOKEN1}/{TOKEN2}/{date_str}"
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = session.get(url, headers=headers, timeout=5)
            data = r.json()
            #with print_lock:
               # print(f"{date_str} attempt {attempt}: {data}")
            if data:
                return (date_str, data)
        except Exception as e:
            with print_lock:
                print(f"Error {date_str}: {e}")
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

# --- Telegram heartbeat la 6h ---
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
