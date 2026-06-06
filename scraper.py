import json
import os
import time
import csv
from datetime import datetime
from playwright.sync_api import sync_playwright

def get_failed_sites():
    """Reads the CSV log and returns a set of names that previously failed."""
    failed = set()
    if os.path.isfile('scrape_log.csv'):
        with open('scrape_log.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['Status'] == 'Failed':
                    failed.add(row['Name'])
    return failed

def log_result(name, url, status, error=""):
    """Appends the result of each scrape to a CSV file."""
    file_exists = os.path.isfile('scrape_log.csv')
    with open('scrape_log.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Name", "URL", "Status", "Error"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), name, url, status, error])

def sanitize_cookies(cookies):
    allowed = ["Strict", "Lax", "None"]
    for cookie in cookies:
        if cookie.get("sameSite") not in allowed:
            cookie["sameSite"] = "None"
    return cookies

def process_url(url, name, cookie_path):
    print(f"Starting process_url for: {name}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        
        if cookie_path and os.path.exists(cookie_path):
            with open(cookie_path, 'r') as f:
                data = json.load(f)
                cookies = data["cookies"] if isinstance(data, dict) and "cookies" in data else data
                context.add_cookies(sanitize_cookies(cookies))
        
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.screenshot(path=f"{name}_initial.jpg", type="jpeg", quality=80)
        
        for i in range(5):
            page.evaluate("window.scrollBy(0, 800)")
            time.sleep(1)
        
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)
        page.screenshot(path=f"{name}_scrolled.jpg", type="jpeg", quality=80, full_page=True)
        browser.close()

if __name__ == "__main__":
    failed_sites = get_failed_sites()
    with open('sites.json', 'r') as f:
        sites = json.load(f)
    
    for site in sites:
        if site['name'] in failed_sites:
            print(f"Skipping {site['name']} (previously failed).")
            continue
            
        try:
            print(f"--- Processing {site['name']} ---")
            process_url(site['url'], site['name'], site.get("cookies"))
            log_result(site['name'], site['url'], "Success")
        except Exception as e:
            print(f"CRITICAL ERROR on {site['name']}: {str(e)}")
            log_result(site['name'], site['url'], "Failed", str(e))
            continue
