# ClubLocker AI Court Booking Assistant

Book squash courts on ClubLocker using natural language. Type "book me a court
tomorrow at 2pm" and it finds open courts, picks one, and makes the reservation.

## Status: archived

This project works end to end, but I stopped development after confirming that
automated booking is against ClubLocker's terms of service. The code is here as
a record of the work, not as a tool to run.

The path forward, if there is one, is permission rather than automation —
sanctioned access through the club or an official API.

## What it does

A request in plain English is parsed by Claude into a structured booking
(date, time, court). Playwright logs into ClubLocker, loads the reservation
grid for that date, and BeautifulSoup extracts which courts are genuinely open
at that hour. You confirm a court, and it fills and submits the booking form.

Runs as a dry run by default — `--book` is required to actually reserve.

## Built

- Login automation and session handling with Playwright
- Reverse-engineered ClubLocker's undocumented reservation grid (no public API)
- Court availability extraction, including free-block vs. per-slot parsing
- Time normalization across formats ("3 PM" → "03:00 PM")
- Natural language parsing via the Claude API
- End-to-end booking with a dry-run guard

## Tech stack

- Python 3.14
- Playwright (browser automation)
- BeautifulSoup4 (HTML parsing)
- Claude API (natural language parsing)

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```
CLUBLOCKER_USERNAME=your_email@example.com
CLUBLOCKER_PASSWORD=your_password
ANTHROPIC_API_KEY=your_api_key
```

## Usage

```bash
# Dry run — fills the form, does not book
python src/main_integration.py "book me a court tomorrow at 2pm"

# Actually reserves
python src/main_integration.py --book "book me a court tomorrow at 2pm"
```

## Known limitations

- Dates are limited to "today" and "tomorrow"; weekday names aren't handled
- The organization ID is hardcoded to Columbia's courts
- Requires a visible browser window — headless login is blocked by a captcha
- Fixed waits rather than real ones, so a slow page load reports no availability

## Recap

What it does: Type “book me a court tomorrow at 2pm,” Claude parses it, Playwright scrapes ClubLocker’s grid and books it.

Hardest bug: Asked for 3 PM, it silently booked 1 PM. The grid renders a whole free stretch as one element listing every time inside it, so my match hit the container instead of the slot. No error — just the wrong answer. Caught it because the form showed the time it picked.

Best find: 3 PM wasn’t bookable at all. Bookings are 45 minutes and the courts were taken at 3:30, so the latest valid start was 2:45. Figured that out from what the dropdown offered.

What went well: Shipped in layers, committed each working. Built the dry-run guard before the code that could book for real.

Why I stopped: Checked the ToS, automated booking isn’t allowed, archived it. Next time I check that first.

## Author

Yusuf Sheikh (Columbia class of 2028 | Computer Science & Varsity Men's Squash)