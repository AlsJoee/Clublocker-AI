# ClubLocker AI Court Booking Assistant

An AI-powered court reservation system for ClubLocker squash courts. Book courts using natural language commands.

## Features ##

- **Web scraping**: Playwright-based automation to extract court availability
- **Natural language parsing**: Claude AI integration to understand booking requests
- **Smart availability**: Shows available courts at requested times
- **Secure credentials**: Environment-based credential management

## Project Status ##

MVP foundation complete (Oct 15, 2026):
- ✅ Login automation with bot detection bypass
- ✅ HTML parsing to extract court availability
- ✅ Time normalization and court matching
- ⏳ LLM integration (ChatGPT)
- ⏳ Booking automation
- ⏳ Frontend UI

## Tech Stack ##

- **Backend**: Python 3.14.2
- **Scraping**: Playwright
- **Parsing**: BeautifulSoup4
- **LLM**: Claude
- **Database**: SQLite (MVP)
- **Frontend**: HTML/CSS/JavaScript

## Setup ##

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies 
pip install -r requirements.txt

# Create .env file with your ClubLocker credentials
CLUBLOCKER_USERNAME=your_email@example.com
CLUBLOCKER_PASSWORD=your_password
```

## Usage ##

```bash
python main.py
```

## Next Steps ##

1. Integrate ClaudeAI for natural language parsing
2. Automate court booking
3. Build chat UI
4. Add multi-player support

## Author ##

Yusuf Sheikh (Columbia class of 2028 | Computer Science & Varsity Men's Squash)