import os
import sys
import asyncio
from datetime import date as date_cls, timedelta
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from llm import parse_booking_request
from scraper import parse_available_courts, find_slot_positions, normalize_time

load_dotenv()

ORG_ID = "903"


def to_iso_date(date_str):
    """Convert 'today'/'tomorrow' to YYYY-MM-DD. Passes through real dates."""
    today = date_cls.today()
    s = (date_str or "").strip().lower()
    if s == "today":
        return today.isoformat()
    if s == "tomorrow":
        return (today + timedelta(days=1)).isoformat()
    return date_str


def choose_court(parsed, slot_map):
    """Decide which court to book. Returns a court number, or None to abort."""
    requested = parsed.get("court")

    if requested is not None:
        if requested in slot_map:
            print(f"Court {requested} is open — as requested.")
            return requested
        print(f"Court {requested} is not available at that time.")

    print(f"\nOpen courts: {sorted(slot_map.keys())}")
    answer = input("Which court? (number, or blank to cancel): ").strip()

    if not answer:
        return None

    try:
        court = int(answer)
    except ValueError:
        print("Not a number — cancelling.")
        return None

    if court not in slot_map:
        print(f"Court {court} isn't open at that time — cancelling.")
        return None

    return court


async def set_start_time(page, target_time):
    """
    Set the 'Start time' dropdown in the booking modal.

    Angular Material select — click to open, then pick from the overlay panel.
    """
    field = page.locator("mat-form-field").filter(has_text="Start time")
    await field.locator("mat-select").click()
    await asyncio.sleep(2)

    for selector in ["mat-option", ".mat-mdc-option", "[role='option']"]:
        options = page.locator(selector)
        count = await options.count()
        print(f"  {selector}: {count} found")

        if count:
            texts = [await options.nth(i).inner_text() for i in range(count)]
            print(f"  options: {texts}")

            for i, text in enumerate(texts):
                if target_time in text:
                    await options.nth(i).click()
                    await asyncio.sleep(1)
                    return

            raise RuntimeError(f"{target_time} not among those options")

    raise RuntimeError("Dropdown never opened — no option elements found")


async def book_court(user_input, dry_run=True):
    parsed = parse_booking_request(user_input)

    if "error" in parsed:
        return {"error": "Could not parse booking request", "success": False}

    print(f"Parsed request: {parsed}")

    username = os.getenv("CLUBLOCKER_USERNAME")
    password = os.getenv("CLUBLOCKER_PASSWORD")
    requested_time = normalize_time(parsed["time"])
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
                f"https://clublocker.com/organizations/{ORG_ID}/reservations/{requested_date}/grid"
            )
            await asyncio.sleep(2)
            await page.evaluate("window.scrollBy(0, 500)")
            await asyncio.sleep(1)

            html = await page.content()
            available_courts = parse_available_courts(html, requested_time)

            if not available_courts:
                return {
                    "error": f"No courts open at {requested_time} on {requested_date}",
                    "success": False
                }

            slot_map = dict(find_slot_positions(html, requested_time))
            court = choose_court(parsed, slot_map)

            if court is None:
                return {"error": "Cancelled — nothing booked", "success": False}

            print(f"\nOpening booking form for court {court}...")
            column = page.locator("div.column.slots").nth(court - 1)
            await column.locator("div.slot").nth(slot_map[court]).click()
            await asyncio.sleep(2)

            print(f"Setting start time to {requested_time}...")
            await set_start_time(page, requested_time)

            await page.screenshot(path="booking_form.png")
            print("Saved booking_form.png")

            if dry_run:
                print("\nDRY RUN — not saving. Check booking_form.png.")
                input("Press Enter to close without booking...")
                return {
                    "parsed_request": parsed,
                    "requested_date": requested_date,
                    "requested_time": requested_time,
                    "chosen_court": court,
                    "booked": False,
                    "success": True
                }

            print("Saving reservation...")
            await page.click("button:has-text('Save')")
            await asyncio.sleep(3)
            await page.screenshot(path="booking_confirmed.png")

            return {
                "parsed_request": parsed,
                "requested_date": requested_date,
                "requested_time": requested_time,
                "chosen_court": court,
                "booked": True,
                "success": True
            }

        except Exception as e:
            return {"error": str(e), "success": False}
        finally:
            await browser.close()


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--book"]
    dry_run = "--book" not in sys.argv

    request = " ".join(args) if args else "book me a court tomorrow at 3pm"

    result = asyncio.run(book_court(request, dry_run=dry_run))

    if result["success"]:
        print(f"\nDate: {result['requested_date']}")
        print(f"Time: {result['requested_time']}")
        print(f"Court: {result['chosen_court']}")
        print(f"Booked: {result['booked']}")
    else:
        print(f"\n{result['error']}")