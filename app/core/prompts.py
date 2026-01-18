# app/core/prompts.py
from datetime import datetime
import pytz

def get_current_date_context() -> str:
    """
    Returns the current date formatted for the LLM prompt.
    Uses Singapore timezone for consistency.
    """
    sg_tz = pytz.timezone('Asia/Singapore')
    now = datetime.now(sg_tz)
    return now.strftime("%A, %B %d, %Y")  # e.g., "Saturday, January 18, 2026"

def get_system_prompt() -> str:
    """
    Generates the system prompt with the current date dynamically injected.
    This ensures relative dates like 'tomorrow', 'next week' are interpreted correctly.
    """
    current_date = get_current_date_context()
    
    return f"""You are an intelligent scheduling assistant.
Today is {current_date}.

Instructions:
1. Extract event details: Title, Start Time, End Time, Location.
2. IMPORTANT DATE HANDLING:
   - "tomorrow" means the day after {current_date}
   - "today" means {current_date}
   - "next Monday/Tuesday/etc." means the next occurrence of that day AFTER today
   - "next week" means 7 days from today
   - "yesterday" is in the past and should be flagged
3. Return the result strictly as a JSON object matching the schema.
4. If end_time or location is missing, set them to null.
5. 'context_notes' must contain the original text.
6. TIMESTAMPS: Always use ISO 8601 format (YYYY-MM-DDTHH:MM:SS) for dates.
7. If no year is specified, assume the current year (2026).
8. If no specific time is given, default to 09:00:00.
"""

# For backward compatibility - dynamic prompt
SYSTEM_PROMPT = get_system_prompt()
