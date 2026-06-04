from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False) # MUST be False so you can see it
    context = browser.new_context()
    page = context.new_page()

    # Manually log in here!
    page.goto("https://www.linkedin.com/login")
    input("Log in manually in the browser, then press Enter here...")

    # Save the session
    context.storage_state(path="auth.json")
    browser.close()
