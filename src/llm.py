import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

def parse_booking_request(user_input):
    """
    Parse natural language booking request using Claude.
    
    Args:
        user_input: String like "book me a court tomorrow at 3pm"
    
    Returns:
        Dictionary with extracted info: {date, time, court}
    """
    
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""Parse this court booking request and extract the information.

User input: "{user_input}"

Extract and return ONLY a JSON object with these fields:
- date: the date requested (e.g., "tomorrow", "2026-10-16", "Friday")
- time: the time requested (e.g., "3 PM", "15:00")
- court: court number if specified (e.g., 2), or null if not specified

Example output:
{{"date": "tomorrow", "time": "3 PM", "court": null}}

Return ONLY the JSON, no other text."""
            }
        ]
    )
    
    # Parse the response
    result_text = message.content[0].text
    print(f"Claude response: {result_text}")
    
    # Convert to dict
    try:
        # Strip markdown code block if present
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
            result_text = result_text.strip()
        
        result = json.loads(result_text)
        return result
    except json.JSONDecodeError:
        return {"error": "Could not parse response"}


if __name__ == "__main__":
    # Test
    test_input = "book me a court tomorrow at 3pm"
    result = parse_booking_request(test_input)
    print(f"Parsed request: {result}")