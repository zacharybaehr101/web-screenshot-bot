import json
import os
import time
import csv
from datetime import datetime
from playwright.sync_api import sync_playwright

def log_result(name, url, status, error=""):
    """Appends the result of each scrape to a CSV file."""
    file_exists = os.path.isfile('scrape_log.csv')
    with open('scrape_log.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Name", "URL", "Status", "Error"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), name, url, status, error])

def process_url(url, name, cookie_path):
    # ... (rest of your existing process_url logic) ...
    # Inside the try/except block in your __main__:
    try:
        process_url(site['url'], site['name'], site.get("cookies"))
        log_result(site['name'], site['url'], "Success")
    except Exception as e:
        log_result(site['name'], site['url'], "Failed", str(e))
        print(f"Error processing {site['name']}: {e}")
