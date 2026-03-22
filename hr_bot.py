from playwright.sync_api import sync_playwright
import time
import os
import random
import json
from datetime import datetime, timedelta

HR_URL = "https://ziegleraerospace.greythr.com/"

USERNAME = os.getenv("HR_USERNAME")
PASSWORD = os.getenv("HR_PASSWORD")

# ===== TIME LOG =====
def log_time():
    utc = datetime.utcnow()
    ist = utc + timedelta(hours=5, minutes=30)
    print("🕒 UTC:", utc)
    print("🕒 IST:", ist)

# ===== HUMAN DELAY =====
def human_delay():
    delay = random.randint(30, 150)  # 30 sec to 5 min
    print(f"⏳ Human delay: {delay}s")
    time.sleep(delay)

# ===== LOGIN CHECK =====
def is_logged_in(page):
    return page.locator("text=Home").count() > 0

# ===== SIGN STATE =====
def is_signed_in(page):
    return page.locator("text=Sign Out").count() > 0

# ===== LOGIN FUNCTION =====
def login(page):
    page.goto(HR_URL)
    page.wait_for_timeout(6000)

    print("🔍 Finding login fields...")

    inputs = page.locator("input")

    inputs.nth(0).fill(USERNAME)
    inputs.nth(1).fill(PASSWORD)

    print("✅ Filled credentials")

    page.locator("button").filter(has_text="Login").click()

    page.wait_for_timeout(6000)
    print("✅ Logged in")

# ===== ENSURE LOGIN =====
def ensure_logged_in(page):
    page.goto(HR_URL)
    page.wait_for_timeout(5000)

    if page.locator("text=Login").count() > 0:
        print("🔐 Logging in...")
        login(page)
    else:
        print("✅ Already logged in")

# ===== HOURS TRACKING =====
FILE = "hours.json"

def load_hours():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return {"total_hours": 0}

def save_hours(data):
    with open(FILE, "w") as f:
        json.dump(data, f)

def update_hours(hours_today=8.5):
    data = load_hours()
    data["total_hours"] += hours_today
    save_hours(data)
    print(f"📊 Total hours: {data['total_hours']}")

# ===== HANDLE ACTION =====
def handle_action(action):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        log_time()
        human_delay()  # 👈 human-like timing

        ensure_logged_in(page)
        page.wait_for_timeout(3000)

        signed_in = is_signed_in(page)

        if action == "login":
            if not signed_in:
                page.wait_for_selector('text=Sign In', timeout=10000)
                page.locator("text=Sign In").first.click()
                print("🟢 Signed In")
            else:
                print("Already signed in")

        elif action == "logout":
            if signed_in:
                page.wait_for_selector('text=Sign Out', timeout=10000)
                page.locator("text=Sign Out").first.click()
                print("🔴 Signed Out")

                # Only count evening logout (important)
                ist_now = datetime.utcnow() + timedelta(hours=5, minutes=30)

                if ist_now.hour >= 18:
                    update_hours(8.5)

            else:
                print("Already signed out")

        browser.close()

# ===== MAIN =====
if __name__ == "__main__":
    action = os.getenv("ACTION")
    handle_action(action)
