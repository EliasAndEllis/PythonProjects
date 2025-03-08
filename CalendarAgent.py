import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os
from dateutil import parser
import datetime

# Scopes for Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Timezone mapping
TIMEZONE_MAP = {
    "toronto time": "America/Toronto",
    "new york time": "America/New_York",
    "london time": "Europe/London",
    "tokyo time": "Asia/Tokyo",
}

# Valid color IDs (1-11)
VALID_COLOR_IDS = [str(i) for i in range(1, 12)]  # "1" to "11"

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

def parse_input(user_input):
    """Parse space-separated input with numeric color IDs."""
    tokens = user_input.lower().strip().split()
    if len(tokens) < 2:
        raise ValueError("Please include at least a date/time and something else (e.g., '03/17 12pm stonemasons')")
    
    # Extract timezone
    timezone = "America/Toronto"  # Default
    timezone_words = []
    for tz_name, tz_value in TIMEZONE_MAP.items():
        tz_parts = tz_name.split()
        if all(part in tokens for part in tz_parts):
            timezone = tz_value
            timezone_words = tz_parts
            break
    
    # Extract color ID
    color_id = None
    for i, token in enumerate(tokens):
        if token in VALID_COLOR_IDS:
            color_id = token
            tokens.pop(i)
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
    
    return {
        'summary': title,
        'start': start_datetime.isoformat(),
        'end': end_datetime.isoformat(),
        'timezone': timezone,
        'colorId': color_id
    }

def create_calendar_event(service, event_details):
    """Create an event on Google Calendar."""
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
    return event['id'], event.get('htmlLink')

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
    return events_result.get('items', [])

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
    return updated_event.get('htmlLink')

def main():
    st.title("Google Calendar AI Agent")

    # Authenticate once and store in session state
    if 'service' not in st.session_state:
        st.session_state.service = authenticate_google_calendar()

    # Action selection
    action = st.radio("Choose Action", ["Create Event", "Modify Event"])

    if action == "Create Event":
        st.subheader("Create a New Event")
        user_input = st.text_input(
            "Enter meeting details (e.g., '03/17 12pm toronto time stonemasons 1')",
            key="create_input"
        )
        if st.button("Create Event"):
            if user_input:
                try:
                    event_details = parse_input(user_input)
                    event_id, event_link = create_calendar_event(st.session_state.service, event_details)
                    st.success(f"Event created: {event_link}")
                    st.write(f"Event ID: {event_id} (save this for future reference)")
                except ValueError as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Please enter event details.")

    elif action == "Modify Event":
        st.subheader("Modify an Existing Event")
        events = list_recent_events(st.session_state.service)
        
        if not events:
            st.write("No upcoming events found.")
        else:
            # Display events in a selectable format
            event_options = [
                f"{event['summary']} - {event['start'].get('dateTime', event['start'].get('date'))} (ID: {event['id']})"
                for event in events
            ]
            selected_event = st.selectbox("Select an event to modify", event_options)
            if selected_event:
                event_id = selected_event.split("ID: ")[1][:-1]  # Extract ID
                new_input = st.text_input(
                    "Enter new details (e.g., '03/18 2pm toronto time painters 5')",
                    key="modify_input"
                )
                if st.button("Modify Event"):
...
