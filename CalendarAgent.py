import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from dateutil import parser
import datetime

SCOPES = ['https://www.googleapis.com/auth/calendar']
TIMEZONE_MAP = {
    "toronto time": "America/Toronto",
    "new york time": "America/New_York",
    "london time": "Europe/London",
    "tokyo time": "Asia/Tokyo",
}
VALID_COLOR_IDS = [str(i) for i in range(1, 12)]

def authenticate_google_calendar():
    creds = None
    if 'credentials' in st.session_state:
        creds = Credentials.from_authorized_user_info(
            st.session_state['credentials'], SCOPES
        )
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            st.session_state['credentials'] = creds.to_json()
        else:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": st.secrets["google"]["client_id"],
                        "client_secret": st.secrets["google"]["client_secret"],
                        "redirect_uris": st.secrets["google"]["redirect_uris"],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token"
                    }
                },
                SCOPES
            )
            auth_url, state = flow.authorization_url(prompt='consent')
            st.session_state['oauth_state'] = state
            st.write(f"Please go to this URL to authorize the app: [{auth_url}]({auth_url})")
            code = st.text_input("Enter the authorization code from the URL:")
            if code:
                flow.fetch_token(code=code)
                creds = flow.credentials
                st.session_state['credentials'] = creds.to_json()
                st.success("Authentication successful! You can now create events.")
    if creds and creds.valid:
        return build('calendar', 'v3', credentials=creds)
    return None

def parse_input(user_input):
    tokens = user_input.lower().strip().split()
    if len(tokens) < 2:
        raise ValueError("Please include at least a date/time and title (e.g., '03/17 12pm meeting')")
    timezone = "America/Toronto"
    timezone_words = []
    for tz_name, tz_value in TIMEZONE_MAP.items():
        tz_parts = tz_name.split()
        if all(part in tokens for part in tz_parts):
            timezone = tz_value
            timezone_words = tz_parts
            break
    color_id = None
    for i, token in enumerate(tokens):
        if token in VALID_COLOR_IDS:
            color_id = token
            tokens.pop(i)
            break
    for word in timezone_words:
        if word in tokens:
            tokens.remove(word)
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
        raise ValueError("Couldn’t find a valid date (e.g., '03/17')")
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
        raise ValueError("Couldn’t parse date and time (e.g., '03/17 12pm')")
    start_datetime = dt if dt.time() != datetime.time(0, 0) else dt.replace(hour=9, minute=0)
    end_datetime = start_datetime + datetime.timedelta(hours=1)
    title = ' '.join(tokens) or "Untitled Meeting"
    return {
        'summary': title,
        'start': start_datetime.isoformat(),
        'end': end_datetime.isoformat(),
        'timezone': timezone,
        'colorId': color_id
    }

def create_calendar_event(service, event_details):
    event = {
        'summary': event_details['summary'],
        'start': {'dateTime': event_details['start'], 'timeZone': event_details['timezone']},
        'end': {'dateTime': event_details['end'], 'timeZone': event_details['timezone']},
        'colorId': event_details['colorId'],
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    return event.get('htmlLink')

st.title("Google Calendar Event Creator")
service = authenticate_google_calendar()
if service:
    user_input = st.text_input("Enter event details (e.g., '03/17 12pm toronto time meeting 1')")
    if st.button("Create Event"):
        try:
            event_details = parse_input(user_input)
            event_link = create_calendar_event(service, event_details)
            st.success(f"Event created! [View it here]({event_link})")
        except ValueError as e:
            st.error(f"Error: {e}")
else:
    st.warning("Please authenticate to create events.")
