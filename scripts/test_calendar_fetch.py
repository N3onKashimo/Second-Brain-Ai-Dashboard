# test_calendar_fetch.py

from calendar_utils import fetch_upcoming_events

events = fetch_upcoming_events(5)
print("📅 Upcoming events:")
for e in events:
    start = e['start'].get('dateTime', e['start'].get('date'))
    print(f" - {e['summary']} at {start}")

