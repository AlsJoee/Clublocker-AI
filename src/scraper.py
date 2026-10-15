from bs4 import BeautifulSoup
import re

def parse_available_courts(html_content, target_time):
    """
    Parse the reservations HTML and find available courts at a specific time.
    
    Args:
        html_content: The HTML from the reservations page
        target_time: Time string like "3 PM" or "1 PM" or "01:00 PM"
    
    Returns:
        List of available court numbers, e.g. [1, 2, 4, 6]
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    slot_columns = soup.find_all('div', class_='column slots')
    
    available_courts = []
    
    # Normalize target time (e.g. "3 PM" -> "03:00 PM")
    target_normalized = normalize_time(target_time)
    
    for court_num, column in enumerate(slot_columns, start=1):
        slots = column.find_all('div', class_='slot')
        
        for slot in slots:
            classes = slot.get('class', [])
            
            # Skip if past or not open
            if 'past' in classes or 'open' not in classes:
                continue
            
            slot_time_elem = slot.find('div', class_='slot-time-start')
            if slot_time_elem:
                time_text = slot_time_elem.get_text(strip=True)
                
                # Extract all times from concatenated string
                times = re.findall(r'\d{1,2}:\d{2}\s(?:AM|PM)', time_text)
                
                # Check if target time is in this slot's times
                if target_normalized in times:
                    available_courts.append(court_num)
                    break  # Found this court at this time, move to next court
    
    return available_courts


def normalize_time(time_str):
    """
    Normalize time string to format HH:00 AM/PM
    E.g. "3 PM" -> "03:00 PM", "1:30 PM" -> "01:30 PM"
    """
    # Remove extra spaces
    time_str = time_str.strip()
    
    # Match hour and AM/PM
    match = re.match(r'(\d{1,2})(?::(\d{2}))?\s*(AM|PM)', time_str, re.IGNORECASE)
    
    if match:
        hour = match.group(1).zfill(2)  # Pad with leading zero
        minute = match.group(2) or "00"
        period = match.group(3).upper()
        return f"{hour}:{minute} {period}"
    
    return time_str  # Return as-is if can't parse


if __name__ == "__main__":
    with open("reservations.html", "r") as f:
        html = f.read()
    
    # Test
    for time in ["1 PM", "2 PM", "3 PM", "01:00 PM"]:
        available = parse_available_courts(html, time)
        print(f"Available courts at {time}: {available}")