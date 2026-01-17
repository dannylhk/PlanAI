# PlanAI

PlanAI is a centralized "Master Chatbot" on Telegram that serves as an intelligent command center for a user's entire schedule. Unlike traditional calendars that are passive storage bins, PlanAI is an active agent that unifies the two most chaotic communication channels for students: Official Emails and Telegram Group Chats.

## Features

### 1. Group Chat Event Listener

- Passively listens to group chats for event mentions
- Automatically extracts event details using LLM
- Checks for schedule conflicts
- Sends private notifications to users

### 2. `/agenda` Command - Daily Schedule Dashboard

The `/agenda` feature transforms the bot from a reactive tool to a proactive assistant, showing users their daily schedule in a beautifully formatted message.

#### Usage

**In Private Chat (DM):**

```
/agenda
```

or natural language:

```
what is my plan today?
```

**In Group Chat:** Command is ignored to protect privacy and prevent chat clutter.

#### Example Output

**Empty State:**

```
🎉 No events scheduled for today. Enjoy your free time!
```

**Populated State:**

```
📅 Your Agenda for Sunday, January 18, 2026

09:00 - CS2103T Lecture
📍 I3 Auditorium

14:00 - Team Meeting
📍 COM1-0210

16:00 - Gym Session

18:00 - Dinner with Friends
📍 UTown
⚠️ CONFLICT
```

#### Design Principles

- **Empty State:** Celebratory, positive message instead of null results
- **Timeline View:** Clean, scannable format with visual hierarchy
- **Bold Times:** Easy to scan down the left side to see daily structure
- **Smart Details:** Location shown with 📍 emoji (only if exists)
- **Conflict Warnings:** Clear ⚠️ indicators for scheduling conflicts
- **Breathing Room:** Double newlines between events prevent visual clutter

#### Implementation Details

**Command Interceptor Pattern** (`app/bot/router.py`)

1. **Input Normalization:** Converts to lowercase, strips whitespace
2. **Guard Clause:** Matches `/agenda` or natural language "my plan"
3. **Date Context:** Generates today's date in Singapore timezone (Asia/Singapore)
4. **Data Retrieval:** Calls `get_events_by_date(user_id, date_string)`
5. **Dispatch:** Formats and sends beautified message

**Visual Formatting** (`app/bot/responses.py`)

- `format_agenda()` function creates HTML-formatted timeline
- Handles empty states with positive UX
- Sanitizes HTML characters to prevent formatting breaks
- 24-hour time format for clarity (09:00, 14:00)

#### Timezone Handling

Uses `pytz` to ensure accurate "today" calculation for Singapore users (NUS):

```python
import pytz
singapore_tz = pytz.timezone('Asia/Singapore')
today = datetime.now(singapore_tz)
```

**Why this matters:** Deployed servers in US/Europe would show wrong "today" without explicit timezone handling.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/dannylhk/PlanAI.git
cd PlanAI
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   Create a `.env` file with:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
OPENAI_API_KEY=your_openai_key_here
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

4. Run the application:

```bash
uvicorn main:app --reload
```

## Testing

### Test /agenda Feature

```bash
python test_agenda.py
```

Tests three scenarios:

1. Empty State - No events scheduled
2. Populated State - Multiple events with various attributes
3. Edge Cases - Special HTML characters, null locations, conflicts

### Test Database

```bash
python test_db.py
```

## Project Structure

```
PlanAI/
├── app/
│   ├── api/          # Webhook endpoint for Telegram
│   ├── bot/          # Bot logic and responses
│   │   ├── router.py      # Message routing and command handling
│   │   ├── responses.py   # Message formatting (including format_agenda)
│   │   └── date_utils.py  # Date/time formatting utilities
│   ├── core/         # LLM and AI agent
│   ├── schemas/      # Pydantic models
│   └── services/     # Database CRUD operations
├── main.py           # FastAPI application entry point
├── requirements.txt  # Python dependencies
└── test_agenda.py    # /agenda feature tests
```

## Architecture

### Message Flow

1. **Telegram → Webhook** (`app/api/webhook.py`)
2. **Webhook → Router** (`app/bot/router.py`)
3. **Router Decision:**
   - Private Chat → `handle_hub_command()` → Commands like `/agenda`
   - Group Chat → `handle_group_listener()` → Event detection

### /agenda Command Flow

1. User sends `/agenda` in private chat
2. `handle_hub_command()` intercepts and normalizes input
3. Generates today's date in Singapore timezone
4. Retrieves events via `get_events_by_date(user_id, date_string)`
5. `format_agenda()` creates beautiful HTML timeline
6. `send_message()` delivers to user

## Integration with Database

The `/agenda` feature is ready for database integration. Replace mock data in `router.py`:

**Current (Mock):**

```python
events = [
    {
        "start_time": "2026-01-18T09:00:00",
        "title": "CS2103T Lecture",
        "location": "I3 Auditorium",
        "conflict": False
    }
]
```

**Production (Database):**

```python
from app.services.crud import get_events_by_date
events = await get_events_by_date(user_id, date_string)
```

**Expected Data Format:**
Each event dictionary must have:

- `start_time`: ISO 8601 timestamp (e.g., "2026-01-18T09:00:00")
- `title`: Event title
- `location`: Event location (can be None)
- `conflict`: Boolean indicating schedule conflicts

## Technologies Used

- **FastAPI:** Web framework for webhook endpoint
- **Telegram Bot API:** Bot interface via `httpx`
- **OpenAI GPT:** Event extraction from natural language
- **Supabase:** PostgreSQL database
- **Pydantic:** Data validation and schemas
- **pytz:** Timezone handling for Singapore time
- **Tavily:** Web enrichment for events

## Contributors

- **Member A:** Database & LLM Integration
- **Member B:** Bot Experience & User Interface (including /agenda feature)

## Development Status

✅ Group Chat Event Listener - Complete  
✅ /agenda Command - Complete (Mock Data)  
🔧 Database Integration - In Progress  
📧 Email Parsing - Planned

## License

MIT License
