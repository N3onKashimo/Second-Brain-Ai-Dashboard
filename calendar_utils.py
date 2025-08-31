# calendar_utils.py

from __future__ import print_function
import datetime
import os.path
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']
CACHE_FILE = "F:/OllamaModels/memory/calendar_cache.json"

def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES
        )
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def fetch_upcoming_events(n=10):
    service = get_calendar_service()
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=n,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    return events_result.get('items', [])

def fetch_all_events(days_past=30, days_future=90):
    """Fetch events between now - N days and now + N days. Save to cache."""
    service = get_calendar_service()
    now = datetime.datetime.utcnow()
    time_min = (now - datetime.timedelta(days=days_past)).isoformat() + 'Z'
    time_max = (now + datetime.timedelta(days=days_future)).isoformat() + 'Z'

    events_result = service.events().list(
        calendarId='primary',
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    # Save to cache
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2)

    return events

def load_cached_events():
    """Return events from local cache."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def add_event(summary, start_datetime, end_datetime):
    service = get_calendar_service()
    event = {
        'summary': summary,
        'start': {'dateTime': start_datetime.isoformat(), 'timeZone': 'America/Chicago'},
        'end': {'dateTime': end_datetime.isoformat(), 'timeZone': 'America/Chicago'},
    }
    return service.events().insert(calendarId='primary', body=event).execute()
