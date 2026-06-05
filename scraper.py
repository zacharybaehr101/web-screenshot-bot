import json
import os
import time
from playwright.sync_api import sync_playwright
from PIL import Image

def process_url(url, name, cookie_path):
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        
        # Setup context arguments
        context_args = {}
        # Only use storage_state if cookie_path is provided and the file exists
        if cookie_path and os.path.exists(cookie_path):
            context_args["storage_state"] = cookie_path
            
        context = browser.new_context(**context_args)
        page = context.new_page()
        
        # Set User-Agent to avoid bot detection
        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        })
        
        print(f"Navigating to {url}...")
        page.goto(url, wait_until="load")

        # 4. Take initial screenshot
        page.screenshot(path=f"{name}_initial.jpg", type="jpeg", quality=80)

        # 5. Slow, deliberate scrolling to trigger lazy-loading
        start_time = time.time()
        while time.time() - start_time < 15:
            page.mouse.wheel(0, 200)
            time.sleep(0.5)
        
        # 6. Final scroll to bottom and screenshot
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)
        page.screenshot(path=f"{name}_scrolled.jpg", type="jpeg", quality=80, full_page=True)
        
        # 7. Resize to thumbnails
        for suffix in ["initial", "scrolled"]:
            file_path = f"{name}_{suffix}.jpg"
            if os.path.exists(file_path):
                img = Image.open(file_path)
                img.thumbnail((800, 800))
                img.save(f"{name}_{suffix}_thumb.jpg", "JPEG", optimize=True)

        browser.close()
        print(f"Finished {name}")

if __name__ == "__main__":
    with open('sites.json', 'r') as f:
        sites = json.load(f)
    
    for site in sites:
        print(f"Starting {site['name']}...")
        cookie_path = site.get("cookies")
        process_url(site['url'], site['name'], cookie_path)
