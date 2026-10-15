import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import time

load_dotenv()
username = os.getenv("CLUBLOCKER_USERNAME")
password = os.getenv("CLUBLOCKER_PASSWORD")

def get_reservations_page(date="2026-10-16"):  # TOMORROW instead of today
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=[
            '--disable-blink-features=AutomationControlled'
        ])
        context = browser.new_context()
        page = context.new_page()
        
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        print("Logging in...")
        page.goto("https://clublocker.com/login")
        time.sleep(1)
        page.fill('input[type="text"]', username)
        page.fill('input[type="password"]', password)
        page.click('button:has-text("LOGIN")')
        time.sleep(4)
        
        print(f"Getting reservations for {date}...")
        page.goto(f"https://clublocker.com/organizations/903/reservations/{date}/grid")
        time.sleep(2)
        
        # Scroll down to load more slots
        print("Scrolling to load more slots...")
        page.evaluate("window.scrollBy(0, 500)")
        time.sleep(1)
        
        # Save HTML
        html_content = page.content()
        with open("reservations.html", "w") as f:
            f.write(html_content)
        print("✓ HTML saved")
        
        # Screenshot
        page.screenshot(path="reservations_page.png")
        print("✓ Screenshot saved")
        
        input("Press Enter to close browser...")
        browser.close()

if __name__ == "__main__":
    get_reservations_page()