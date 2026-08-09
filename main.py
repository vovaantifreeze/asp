import os
import requests
from datetime import datetime

# --- ASP tokens ---
TOKEN1 = os.getenv("ASP_TOKEN1")
TOKEN2 = os.getenv("ASP_TOKEN2")
TOKEN3 = os.getenv("ASP_TOKEN3")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*"
}

date_str = "2026-09-11"
url = f"https://eservicii.gov.md/asp/dimtcca/api/qmatic/times/{TOKEN1}/{TOKEN2}/{date_str}/{TOKEN3}"

print("--- DIAGNOSTIC START ---")
print(f"Testing URL: https://eservicii.gov.md/asp/dimtcca/api/qmatic/times/TOKEN1/TOKEN2/{date_str}/TOKEN3")
print(f"TOKEN1 set? {bool(TOKEN1)}")
print(f"TOKEN2 set? {bool(TOKEN2)}")
print(f"TOKEN3 set? {bool(TOKEN3)}")

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"HTTP Status Code: {response.status_code}")
    print(f"Response Content: {response.text}")
    print(f"Parsed JSON: {response.json()}")
except Exception as e:
    print(f"Request Error: {type(e).__name__} - {e}")

print("--- DIAGNOSTIC END ---")
