import json
import os
import time
from playwright.sync_api import sync_playwright

def process_url(url, name, cookie_path):
    with sync_playwright() as p:
        # Launch browser with a persistent context if cookies are provided
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        
        # Load cookies if they exist
        if cookie_path and os.path.exists(cookie_path):
            with open(cookie_path, 'r') as f:
                cookies = json.load(f)
                context.add_cookies(cookies)
        
        page = context.new_page()
        print(f"Navigating to {url}...")
        page.goto(url, wait_until="networkidle") # Wait for all network activity to stop

        # 5. Robust Scroll Logic (Force trigger lazy-load)
        # We scroll to the bottom in 3 big chunks to force content discovery
        for i in range(3):
            page.evaluate("window.scrollBy(0, window.innerHeight)")
            time.sleep(3) # Wait for content to paint
        
        # 6. Final screenshot
        page.screenshot(path=f"{name}_scrolled.jpg", type="jpeg", quality=80, full_page=True)
        
        browser.close()
        print(f"Finished {name}")

if __name__ == "__main__":
    with open('sites.json', 'r') as f:
        sites = json.load(f)
    
    for site in sites:
        cookie_path = site.get("cookies")
        process_url(site['url'], site['name'], cookie_path)
