import time
import json
from playwright.sync_api import sync_playwright
from PIL import Image

def process_url(url, name):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="load")

        # 1. Take initial "browser window" screenshot
        page.screenshot(path=f"{name}_initial.jpg", type="jpeg", quality=80)

        # 2. Timed 12-second scroll
        start_time = time.time()
        while time.time() - start_time < 12:
            page.mouse.wheel(0, 500)
            time.sleep(1) # Scroll every second
        
        # 3. Take second "after-scroll" screenshot
       # Updated to capture the entire scrollable area of the website
page.screenshot(path=f"{name}_scrolled.jpg", type="jpeg", quality=80, full_page=True)
        
        # 4. Resize both to thumbnails for lighter storage
        for suffix in ["initial", "scrolled"]:
            img = Image.open(f"{name}_{suffix}.jpg")
            img.thumbnail((800, 800)) # Resizes maintaining aspect ratio
            img.save(f"{name}_{suffix}_thumb.jpg", "JPEG", optimize=True)

        browser.close()
        print(f"Finished {name}")

# Load the session state
context = browser.new_context(storage_state="auth.json")
page = context.new_page()

# Now, when you visit, you are already logged in!
page.goto("https://www.linkedin.com/feed")

# Test locally with one URL
if __name__ == "__main__":
    process_url("https://www.linkedin.com", "linkedin_test")

    import json

if __name__ == "__main__":
    with open('sites.json', 'r') as f:
        sites = json.load(f)
    
    for site in sites:
        print(f"Starting {site['name']}...")
        process_url(site['url'], site['name'])
