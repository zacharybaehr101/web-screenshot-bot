import json
import os
import time
from playwright.sync_api import sync_playwright

def sanitize_cookies(cookies):
    """Ensures all sameSite values are Strict, Lax, or None."""
    allowed = ["Strict", "Lax", "None"]
    for cookie in cookies:
        if cookie.get("sameSite") not in allowed:
            cookie["sameSite"] = "None"
    return cookies

def process_url(url, name, cookie_path):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        
        # Load and sanitize cookies if provided
        if cookie_path and os.path.exists(cookie_path):
            with open(cookie_path, 'r') as f:
                data = json.load(f)
                cookies = data["cookies"] if isinstance(data, dict) and "cookies" in data else data
                context.add_cookies(sanitize_cookies(cookies))
        
        page = context.new_page()
        print(f"Navigating to {url}...")
        page.goto(url, wait_until="domcontentloaded")

        # 1. Take initial screenshot (top of page)
        page.screenshot(path=f"{name}_initial.jpg", type="jpeg", quality=80)

        # 2. Aggressive scroll to force lazy-load
        for i in range(5):
            page.evaluate("window.scrollBy(0, 800)")
            time.sleep(2)
        
        # 3. Final scroll and screenshot
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)
        page.screenshot(path=f"{name}_scrolled.jpg", type="jpeg", quality=80, full_page=True)
        
        browser.close()
        print(f"Finished {name}")

if __name__ == "__main__":
    with open('sites.json', 'r') as f:
        sites = json.load(f)
    
    for site in sites:
        process_url(site['url'], site['name'], site.get("cookies"))
