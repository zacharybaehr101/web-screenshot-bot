import time
import json
from playwright.sync_api import sync_playwright
from PIL import Image

def process_url(url, name):
    with sync_playwright() as p:
        # 1. Launch browser
        browser = p.chromium.launch(headless=True)
        
        # 2. Handle Authentication (New block for GitHub Secret)
        if "AUTH_JSON" in os.environ:
            with open("auth.json", "w") as f:
                f.write(os.environ["AUTH_JSON"])
        
        # 3. Setup context with storage_state
        context_args = {}
        if os.path.exists("auth.json"):
            context_args["storage_state"] = "auth.json"
            
        context = browser.new_context(**context_args)
        page = context.new_page()
        
        print(f"Navigating to {url}...")
        page.goto(url, wait_until="load")

        # 4. Take initial screenshot
        page.screenshot(path=f"{name}_initial.jpg", type="jpeg", quality=80)

        # 5. Timed scroll
        start_time = time.time()
        while time.time() - start_time < 12:
            page.mouse.wheel(0, 500)
            time.sleep(1)
        
        # 6. Take FULL PAGE after-scroll screenshot
        page.screenshot(path=f"{name}_scrolled.jpg", type="jpeg", quality=80, full_page=True)
        
        # 7. Resize to thumbnails
        for suffix in ["initial", "scrolled"]:
            if os.path.exists(f"{name}_{suffix}.jpg"):
                img = Image.open(f"{name}_{suffix}.jpg")
                img.thumbnail((800, 800))
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
