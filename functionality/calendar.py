import os
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


# Calendar colorId
# 0 green default
# 1 purple
# 2 green teal
# 3 pink
# 4 red
# 5 yellow

def create_google_calendar_event(title, description, date, time, duration=1, color_id=0 | 9):
    # TODO: handle reminders using google-reminders-cli
    # https://github.com/jonahar/google-reminders-cli/tree/master
    SCOPES = ['https://www.googleapis.com/auth/calendar']
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

    # Build the Calendar API service object
    service = build('calendar', 'v3', credentials=creds)

    # Calculate event start and end datetime objects
    start_datetime = datetime.strptime(f'{date} {time}', '%Y-%m-%d %H:%M')
    end_datetime = start_datetime + timedelta(hours=duration)

    # Form the event data
    event = {
        'summary': title,  # Event title
        'description': description,  # Event description
        'start': {
            'dateTime': start_datetime.isoformat(),
            'timeZone': 'America/Bogota'  # User Timezone
        },
        'end': {
            'dateTime': end_datetime.isoformat(),
            'timeZone': 'America/Bogota'  # User Timezone
        },
        'colorId': color_id,
    }
    # Create the event
    event = service.events().insert(calendarId='primary', body=event).execute()
    print(f'Event created: {event.get("htmlLink")}')


# create_google_calendar_event(
#     title="Project Review",
#     description="Discuss progress and next steps for Q2 launch",
#     date="2024-04-07",
#     time="14:00",
#     duration=1
# )

# TODO: be able to retrieve events
#   - Your next event
#   - Next "time" events about x thing
#   - Modify your next eent.
