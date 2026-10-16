import os
import asyncio
from datetime import date as date_cls, timedelta
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from llm import parse_booking_request
from scraper import parse_available_courts

load_dotenv()


def to_iso_date(date_str):
    """Convert 'today'/'tomorrow' to YYYY-MM-DD. Passes through real dates."""
    today = date_cls.today()
    s = (date_str or "").strip().lower()
    if s == "today":
        return today.isoformat()
    if s == "tomorrow":
        return (today + timedelta(days=1)).isoformat()
    return date_str


async def book_court(user_input):
    """
    Main integration: parse booking request and fetch available courts.

    Args:
        user_input: String like "book me a court tomorrow at 3pm"

    Returns:
        Dictionary with parsed request and available courts
    """

    # Step 1: Parse the user input with LLM
    parsed = parse_booking_request(user_input)

    if "error" in parsed:
        return {"error": "Could not parse booking request", "success": False}

    print(f"Parsed request: {parsed}")

    username = os.getenv("CLUBLOCKER_USERNAME")
    password = os.getenv("CLUBLOCKER_PASSWORD")
    requested_time = parsed["time"]
    requested_date = to_iso_date(parsed["date"])

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context()
        page = await context.new_page()

        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)

        try:
            print("Logging in...")
            await page.goto("https://clublocker.com/login")
            await asyncio.sleep(1)
            await page.fill('input[type="text"]', username)
            await page.fill('input[type="password"]', password)
            await page.click('button:has-text("LOGIN")')
            await asyncio.sleep(4)

            print(f"Getting reservations for {requested_date}...")
            await page.goto(
                f"https://clublocker.com/organizations/903/reservations/{requested_date}/grid"
            )
            await asyncio.sleep(2)

            # Scroll to load more slots
            await page.evaluate("window.scrollBy(0, 500)")
            await asyncio.sleep(1)

            html = await page.content()
            available_courts = parse_available_courts(html, requested_time)

            return {
                "parsed_request": parsed,
                "requested_date": requested_date,
                "requested_time": requested_time,
                "available_courts": available_courts,
                "success": True
            }

        except Exception as e:
            return {"error": str(e), "success": False}
        finally:
            await browser.close()


if __name__ == "__main__":
    test_input = "book me a court tomorrow at 3pm"
    result = asyncio.run(book_court(test_input))

    if result["success"]:
        print(f"\nParsed: {result['parsed_request']}")
        print(f"Date: {result['requested_date']}")
        print(f"Time: {result['requested_time']}")
        print(f"Available courts: {result['available_courts']}")
    else:
        print(f"Error: {result['error']}")