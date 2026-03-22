from playwright.sync_api import sync_playwright
import time
import os
from datetime import datetime, timedelta

HR_URL = "https://ziegleraerospace.greythr.com/"

USERNAME = os.getenv("HR_USERNAME")
PASSWORD = os.getenv("HR_PASSWORD")

# ===== TIME LOG =====
def log_time():
    utc = datetime.utcnow()
    ist = utc + timedelta(hours=5, minutes=30)
    print("🕒 UTC Time:", utc)
    print("🕒 IST Time:", ist)

# ===== LOGIN CHECK =====
def is_logged_in(page):
    return page.locator("text=Home").count() > 0

# ===== SIGN STATE =====
def is_signed_in(page):
    return page.locator("text=Sign Out").count() > 0

# ===== LOGIN FUNCTION =====
def login(page):
    page.goto(HR_URL)

    # wait for page to fully load
    page.wait_for_timeout(6000)

    print("🔍 Finding login fields...")

    # Find ALL input boxes
    inputs = page.locator("input")

    # Fill username (first input)
    inputs.nth(0).fill(USERNAME)

    # Fill password (second input)
    inputs.nth(1).fill(PASSWORD)

    print("✅ Filled credentials")

    # Click login button (flexible)
    page.locator("button").filter(has_text="Login").click()

    page.wait_for_timeout(6000)

    print("✅ Logged in")

# ===== ENSURE LOGIN =====
def ensure_logged_in(page):
    page.goto(HR_URL)
    page.wait_for_timeout(3000)

    if not is_logged_in(page):
        print("🔐 Logging in...")
        login(page)
    else:
        print("✅ Already logged in")

# ===== HANDLE ACTION =====
def handle_action(action):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        log_time()
        ensure_logged_in(page)

        page.wait_for_timeout(3000)

        signed_in = is_signed_in(page)

        if action == "login":
            if not signed_in:
                page.wait_for_selector('button:has-text("Sign In")', timeout=10000)
                page.click('button:has-text("Sign In")')
                print("🟢 Signed In")
            else:
                print("Already signed in")

        elif action == "logout":
            if signed_in:
                page.wait_for_selector('button:has-text("Sign Out")', timeout=10000)
                page.click('button:has-text("Sign Out")')
                print("🔴 Signed Out")
            else:
                print("Already signed out")

        browser.close()

# ===== MAIN =====
if __name__ == "__main__":
    action = os.getenv("ACTION")
    handle_action(action)
