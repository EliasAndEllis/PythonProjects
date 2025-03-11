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

def check_for_duplicate(service, event_details):
    """Check if an event with the same normalized title, date, and time exists."""
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    end_of_next_year = datetime.datetime(datetime.datetime.now().year + 1, 12, 31, 23, 59, 59).isoformat() + 'Z'

    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        timeMax=end_of_next_year,
        q=event_details['summary'],  # Search by raw title
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    tz = pytz.timezone(event_details['timezone'])
    new_start_dt_naive = datetime.datetime.fromisoformat(event_details['start'].replace('Z', '+00:00'))
    new_start_dt = tz.localize(new_start_dt_naive)
    new_title_normalized = normalize_title(event_details['summary'])

    for event in events:
        existing_start = event['start'].get('dateTime', event['start'].get('date'))
        existing_dt = datetime.datetime.fromisoformat(existing_start.replace('Z', '+00:00'))
        if existing_dt.tzinfo is None:
            existing_dt = pytz.UTC.localize(existing_dt)
        
        existing_title_normalized = normalize_title(event['summary'])
        
        if (existing_title_normalized == new_title_normalized and
            abs((existing_dt - new_start_dt).total_seconds()) < 60):
            print(f"Debug: Duplicate found - Existing: {event['summary']} at {existing_start}, New: {event_details['summary']} at {new_start_dt}")
            return True
    print(f"Debug: No duplicate found for '{event_details['summary']}' at {new_start_dt}")
    return False

def create_calendar_event(service, event_details):
    """Create an event on Google Calendar if it doesn’t already exist."""
    if check_for_duplicate(service, event_details):
        print(f"Event '{event_details['summary']}' at {event_details['start']} already exists.")
        return None
    
    event = {
        'summary': event_details['summary'],
        'start': {
            'dateTime': event_details['start'],
            'timeZone': event_details['timezone'],
        },
        'end': {
            'dateTime': event_details['end'],
            'timeZone': event_details['timezone'],
        },
        'colorId': event_details['colorId'],
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    print(f"Event created: {event.get('htmlLink')}")
    return event['id']

def list_recent_events(service, num_events=5):
    """List recent events with their IDs."""
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=num_events,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    
    if not events:
        print("No upcoming events found.")
        return None
    
    print("\nRecent Events:")
    for i, event in enumerate(events, 1):
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(f"{i}. {event['summary']} - {start} (ID: {event['id']})")
    return events

def modify_calendar_event(service, event_id, event_details):
    """Modify an existing event on Google Calendar."""
    event = {
        'summary': event_details['summary'],
        'start': {
            'dateTime': event_details['start'],
            'timeZone': event_details['timezone'],
        },
        'end': {
            'dateTime': event_details['end'],
            'timeZone': event_details['timezone'],
        },
        'colorId': event_details['colorId'],
    }
    updated_event = service.events().patch(
        calendarId='primary',
        eventId=event_id,
        body=event
    ).execute()
    print(f"Event updated: {updated_event.get('htmlLink')}")

def main():
    service = authenticate_google_calendar()
    
    while True:
        action = input("\nChoose action: 'create', 'modify', or 'exit': ").lower()
        
        if action == 'exit':
            print("Goodbye!")
            break
        
        elif action == 'create':
            user_input = input("Enter meeting details (e.g., '03/17 12pm toronto time roofers meeting'): ")
            try:
                event_details = parse_input(user_input)
                event_id = create_calendar_event(service, event_details)
                if event_id:
                    print(f"Event ID: {event_id} (save this to modify later)")
            except ValueError as e:
                print(f"Error: {e}")
        
        elif action == 'modify':
            events = list_recent_events(service)
            if not events:
                continue
            
            choice = input("Enter the number of the event to modify (1-5) or 'back' to return: ")
            if choice.lower() == 'back':
                continue
            try:
                event_index = int(choice) - 1
                if 0 <= event_index < len(events):
                    event_id = events[event_index]['id']
                    new_input = input("Enter new details (e.g., '03/18 2pm toronto time painters'): ")
                    try:
                        event_details = parse_input(new_input)
                        modify_calendar_event(service, event_id, event_details)
                    except ValueError as e:
                        print(f"Error: {e}")
                else:
                    print("Invalid event number.")
            except ValueError:
                print("Please enter a valid number or 'back'.")
        
        else:
            print("Event already exists. Choose 'create', 'modify', or 'exit'.")

if __name__ == '__main__':
    main()
