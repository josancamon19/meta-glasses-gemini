import base64
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

# {
#   "installed": {
#     "client_id": "740507740098-e2nqpm160vrnuskd27i90bi9t8tp987i.apps.googleusercontent.com",
#     "project_id": "meta-rayban-glasses",
#     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#     "token_uri": "https://oauth2.googleapis.com/token",
#     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#     "client_secret": "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",
#     "redirect_uris": [
#       "http://localhost"
#     ]
#   }
# }
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
            credentials_data_base64 = os.getenv('OAUTH_CREDENTIALS_ENCODED')  # base64 encoded credentials.json
            credentials_data = base64.b64decode(credentials_data_base64).decode('utf-8')
            with open('credentials.json', 'w') as credentials:
                credentials.write(credentials_data)

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


create_google_calendar_event(
    title="Project Review",
    description="Discuss progress and next steps for Q2 launch",
    date="2024-04-10",
    time="14:00",
    duration=1
)

# TODO: be able to retrieve events
#   - Your next event
#   - Next "time" events about x thing
#   - Modify your next eent.
