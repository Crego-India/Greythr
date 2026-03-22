from playwright.sync_api import sync_playwright
import time
from datetime import datetime

HR_URL = "https://ziegleraerospace.greythr.com/"

import os
USERNAME = os.getenv("HR_USERNAME")
PASSWORD = os.getenv("HR_PASSWORD")

def is_logged_in(page):
    return page.locator("text=Home").count() > 0

def is_signed_in(page):
    return page.locator("text=Sign Out").count() > 0

def login(page):
    page.goto(HR_URL)
    page.fill('input[placeholder="Login ID"]', USERNAME)
    page.fill('input[type="password"]', PASSWORD)
    page.click('button:has-text("Login")')
    time.sleep(5)

def ensure_logged_in(page):
    page.goto(HR_URL)
    if not is_logged_in(page):
        login(page)

def handle_action(action):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        ensure_logged_in(page)

        signed_in = is_signed_in(page)

        if action == "login" and not signed_in:
            page.click('button:has-text("Sign In")')
            print("Signed In")

        elif action == "logout" and signed_in:
            page.click('button:has-text("Sign Out")')
            print("Signed Out")

        else:
            print("Already correct state")

        browser.close()

if __name__ == "__main__":
    action = os.getenv("ACTION")
    handle_action(action)
