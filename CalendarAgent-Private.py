from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os
from dateutil import parser
import datetime
import pytz

# Scopes for Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Timezone mapping
TIMEZONE_MAP = {
    "toronto time": "America/Toronto",
    "new york time": "America/New_York",
    "london time": "Europe/London",
    "tokyo time": "Asia/Tokyo",
}

# Keyword to color mapping (predefined)
KEYWORD_COLOR_MAP = {
    "roofers": "5",        # Banana
    "construct": "6",      # Tangerine (includes "construction")
    "stone": "7",          # Peacock (includes "stonemasons")
    "welders": "10"        # Basil
}

# Synonyms mapping for normalization (case-insensitive)
SYNONYM_MAP = {
    "construction": "construct",
    "stonemasons": "stone"
}

def authenticate_google_calendar():
    """Authenticate with Google Calendar API and return the service object."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('calendar', 'v3', credentials=creds)
    return service

def normalize_title(title):
    """Normalize title by mapping synonyms to a canonical keyword."""
    title_lower = title.lower()
    for synonym, canonical in SYNONYM_MAP.items():
        if synonym in title_lower:
            title_lower = title_lower.replace(synonym, canonical)
    return title_lower

def parse_input(user_input):
    """Parse space-separated input and assign color based on title keywords."""
    tokens = user_input.lower().strip().split()
    if len(tokens) < 2:
        raise ValueError("Please include at least a date/time and something else (e.g., '03/17 12pm roofers')")
    
    # Extract timezone
    timezone = "America/Toronto"  # Default
    timezone_words = []
    for tz_name, tz_value in TIMEZONE_MAP.items():
        tz_parts = tz_name.split()
        if all(part in tokens for part in tz_parts):
            timezone = tz_value
            timezone_words = tz_parts
            break
    
    # Remove timezone tokens
    for word in timezone_words:
        if word in tokens:
            tokens.remove(word)
    
    # Parse date and time
    date_time_str = ""
    for i, token in enumerate(tokens):
        try:
            dt = parser.parse(token, fuzzy=True, dayfirst=False)
            date_time_str = token
            tokens.pop(i)
            break
        except ValueError:
            continue
    
    if not date_time_str:
        raise ValueError("Couldn’t find a valid date (e.g., '03/17').")
    if i < len(tokens) - 1:
        try:
            dt = parser.parse(f"{date_time_str} {tokens[i]}", fuzzy=True, dayfirst=False)
            date_time_str = f"{date_time_str} {tokens.pop(i)}"
        except ValueError:
            pass
    
    try:
        dt = parser.parse(date_time_str, fuzzy=True, dayfirst=False)
        if dt.year == datetime.datetime.now().year and date_time_str.lower() not in [str(datetime.datetime.now().year), str(datetime.datetime.now().year)[2:]]:
            dt = dt.replace(year=datetime.datetime.now().year)
        if dt < datetime.datetime.now():
            dt = dt.replace(year=datetime.datetime.now().year + 1)
    except ValueError:
        raise ValueError("Couldn’t parse date and time (e.g., '03/17 12pm').")
    
    start_datetime = dt if dt.time() != datetime.time(0, 0) else dt.replace(hour=9, minute=0)
    end_datetime = start_datetime + datetime.timedelta(hours=1)
    
    # Remaining tokens are the title
    title = ' '.join(tokens) or "Untitled Meeting"
    
    # Assign color based on keywords in title
    color_id = None
    title_lower = title.lower()
    for keyword, color in KEYWORD_COLOR_MAP.items():
        if keyword in title_lower:
            color_id = color
            break
    
    return {
        'summary': title,
        'start': start_datetime.isoformat(),
        'end': end_datetime.isoformat(),
        'timezone': timezone,
        'colorId': color_id
    }

def check_for_duplicate(service, event_details
