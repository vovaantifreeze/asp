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

# --- ASP Tokens ---
TOKEN1 = os.getenv("ASP_TOKEN1") # publicServiceId
TOKEN2 = os.getenv("ASP_TOKEN2") # publicLocationId
TOKEN3 = os.getenv("ASP_TOKEN3") # requestId

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": "https://eservicii.gov.md",
    "Referer": "https://eservicii.gov.md/"
}

MAX_RETRIES = 3
RETRY_DELAY = 1.0
MAX_WORKERS = 3
print_lock = Lock()
session = requests.Session()

# --- Zile Active (24-28 August + 25 Septembrie 2026) ---
active_dates = [
    datetime(2026, 8, 24),
    datetime(2026, 8, 25),
    datetime(2026, 8, 26),
    datetime(2026, 8, 27),
    datetime(2026, 8, 28),
    datetime(2026, 9, 25)
]

# --- Date Check Function (Metoda POST) ---
def check_date(date):
    date_str = date.strftime("%Y-%m-%d")
    url = "https://eservicii.gov.md/asp/dimtcca/api/qmatic/times"
    
    payload = {
        "publicServiceId": TOKEN1,
        "publicLocationId": TOKEN2,
        "requestId": TOKEN3,
        "date": date_str
    }
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = session.post(url, json=payload, headers=headers, timeout=5)
            
            if r.status_code == 200:
                text = r.text.strip()
                if text and (text.startswith("[") or text.startswith("{")):
                    data = r.json()
                    if data: 
                        return (date_str, data)
            elif r.status_code == 429:
                time.sleep(2.0)
                
        except Exception as e:
            with print_lock:
                print(f"Error [{date_str}] attempt {attempt}: {e}")
                
        time.sleep(RETRY_DELAY)
    return None

def run_check_loop():
    while True:
        print(f"\nChecking... {datetime.now()}")
        found_any = False
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(check_date, d) for d in active_dates]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    found_any = True
                    date_str, data = result
                    
                    times_list = [item.get("time") for item in data if isinstance(item, dict) and "time" in item]
                    formatted_times = ", ".join(times_list) if times_list else str(data)
                    
                    message = f"🚨 SLOT GĂSIT! 🚨\nData: {date_str}\nOre disponibile: {formatted_times}"
                    print(message)
                    send_telegram(message)
                    
        if not found_any:
            print("Nimic disponibil")
            
        time.sleep(8)

# --- Telegram Heartbeat (12h) ---
def heartbeat_loop():
    while True:
        send_telegram("Botul rulează ✔")
        time.sleep(43200)

# --- Flask Server ---
app = Flask("ASPChecker")

@app.route("/")
def home():
    return "ASP Checker rulează 24/7 ✅"

# --- Start Threads ---
Thread(target=run_check_loop, daemon=True).start()
Thread(target=heartbeat_loop, daemon=True).start()

# --- Start Flask ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
    
