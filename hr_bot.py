from playwright.sync_api import sync_playwright
import time
import os
import random
import json
from datetime import datetime, timedelta

HR_URL = "https://ziegleraerospace.greythr.com/"

USERNAME = os.getenv("HR_USERNAME")
PASSWORD = os.getenv("HR_PASSWORD")

FILE = "hours.json"

# ===== TIME =====
def get_ist():
    return datetime.utcnow() + timedelta(hours=5, minutes=30)

def log_time():
    utc = datetime.utcnow()
    ist = get_ist()
    print("🕒 UTC:", utc)
    print("🕒 IST:", ist)

# ===== HUMAN DELAY =====
def human_delay():
    ist = get_ist()

    if ist.hour == 9 or (ist.hour < 13 and ist.hour >= 9):
        # Morning window: 9:28 – 9:35
        target_minute = random.randint(28, 35)
        target_second = random.randint(0, 59)
        target = ist.replace(hour=9, minute=target_minute, second=target_second, microsecond=0)

        wait = (target - ist).total_seconds()
        if wait > 0:
            print(f"⏳ Waiting until 09:{target_minute:02d}:{target_second:02d} IST ({int(wait)}s)")
            time.sleep(wait)
        else:
            print("⏳ Already in morning window, proceeding")

    elif ist.hour == 13 or (ist.hour == 14 and ist.minute < 5):
        # Afternoon window: 13:55 – 14:00
        target_minute = random.randint(55, 59)
        target_second = random.randint(0, 59)
        target = ist.replace(hour=13, minute=target_minute, second=target_second, microsecond=0)

        wait = (target - ist).total_seconds()
        if wait > 0:
            print(f"⏳ Waiting until 13:{target_minute:02d}:{target_second:02d} IST ({int(wait)}s)")
            time.sleep(wait)
        else:
            print("⏳ Already in afternoon window, proceeding")

    elif ist.hour >= 18:
        delay = random.randint(0, 900)
        print(f"⏳ Evening delay: {delay}s")
        time.sleep(delay)

    else:
        delay = random.randint(30, 300)
        print(f"⏳ Default delay: {delay}s")
        time.sleep(delay)

# ===== DATA HANDLING =====
def load_data():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return {"months": {}}

def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_today():
    now = get_ist()
    return now.strftime("%Y-%m-%d"), now

def get_month_key(now):
    return now.strftime("%Y-%m")

# ===== RECORD LOGS =====
def record_time(event_type):
    data = load_data()
    today, now = get_today()
    month_key = get_month_key(now)

    if month_key not in data["months"]:
        data["months"][month_key] = {
            "days": {},
            "total_hours": 0
        }

    month = data["months"][month_key]

    if today not in month["days"]:
        month["days"][today] = {
            "morning": {},
            "afternoon": {},
            "total": 0
        }

    day = month["days"][today]
    time_str = now.strftime("%H:%M:%S")

    if event_type == "login_morning":
        day["morning"]["in"] = time_str

    elif event_type == "logout_lunch":
        day["morning"]["out"] = time_str
        if "in" in day["morning"]:
            t1 = datetime.strptime(day["morning"]["in"], "%H:%M:%S")
            t2 = datetime.strptime(time_str, "%H:%M:%S")
            hours = (t2 - t1).seconds / 3600
            day["morning"]["hours"] = round(hours, 2)

    elif event_type == "login_afternoon":
        day["afternoon"]["in"] = time_str

    elif event_type == "logout_evening":
        day["afternoon"]["out"] = time_str
        if "in" in day["afternoon"]:
            t1 = datetime.strptime(day["afternoon"]["in"], "%H:%M:%S")
            t2 = datetime.strptime(time_str, "%H:%M:%S")
            hours = (t2 - t1).seconds / 3600
            day["afternoon"]["hours"] = round(hours, 2)

        total = 0
        if "hours" in day["morning"]:
            total += day["morning"]["hours"]
        if "hours" in day["afternoon"]:
            total += day["afternoon"]["hours"]

        day["total"] = round(total, 2)

        month["total_hours"] = round(
            sum(d.get("total", 0) for d in month["days"].values()), 2
        )

    save_data(data)
    print(f"📊 Updated {today} in {month_key}")

# ===== LOGIN CHECK =====
def is_logged_in(page):
    return page.locator("text=Home").count() > 0

def is_signed_in(page):
    return page.locator("text=Sign Out").count() > 0

# ===== LOGIN =====
def login(page):
    page.goto(HR_URL)
    page.wait_for_timeout(6000)

    inputs = page.locator("input")

    if inputs.count() >= 2:
        inputs.nth(0).fill(USERNAME)
        inputs.nth(1).fill(PASSWORD)
    else:
        print("❌ Login fields not found")
        return

    page.wait_for_selector('button:has-text("Login")', timeout=10000)
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

# ===== MAIN ACTION =====
def handle_action(action):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        log_time()
        human_delay()

        ensure_logged_in(page)
        page.wait_for_timeout(3000)

        signed_in = is_signed_in(page)
        ist_now = get_ist()

        if action == "login":
            if not signed_in:
                page.wait_for_selector("text=Sign In", timeout=10000)
                page.locator("text=Sign In").first.click()

                if ist_now.hour < 13:
                    record_time("login_morning")
                else:
                    record_time("login_afternoon")

                print("🟢 Signed In")
            else:
                print("Already signed in")

        elif action == "logout":
            if signed_in:
                page.wait_for_selector("text=Sign Out", timeout=10000)
                page.locator("text=Sign Out").first.click()

                if ist_now.hour < 15:
                    record_time("logout_lunch")
                else:
                    record_time("logout_evening")

                print("🔴 Signed Out")
            else:
                print("Already signed out")

        browser.close()

# ===== ENTRY =====
if __name__ == "__main__":
    action = os.getenv("ACTION")
    handle_action(action)
