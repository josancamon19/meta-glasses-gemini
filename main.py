from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import PlainTextResponse

from functionality.calendar import create_google_calendar_event
from functionality.image import logic_for_prompt_before_image, retrieve_calories_from_image
from functionality.notion_ import *
from functionality.search import *
from utils.whatsapp import send_whatsapp_threaded
from utils.gemini import *

app = FastAPI()
ok = {'status': 'Ok'}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.messenger.com", "https://www.facebook.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/webhook', response_class=PlainTextResponse)
def webhook_verification(request: Request):
    if request.query_params.get('hub.mode') == 'subscribe' and request.query_params.get(
            'hub.verify_token') == os.getenv('WHATSAPP_WEBHOOK_VERIFICATION_TOKEN'):
        return request.query_params.get('hub.challenge')
    else:
        raise HTTPException(status_code=400, detail="Bad Request")


@app.post('/webhook')
def receive_whatsapp_message(request: Request, data: dict):
    # TODO: webhook authentication handling
    message = data['entry'][0]['changes'][0]['value'].get('messages', [{}])[0]
    threading.Thread(target=logic, args=(message,)).start()
    return ok


def logic(message: dict):
    if not message:
        return ok
    # message['id'] # message id to redis set, if in set, skip
    # e.g. wamid.HBgMNTczNTA0MzQyMjYyFQIAEhgUM0EzNzk5MzY2MzBGQ0Q4NzJDQzgA

    if message['type'] == 'image':
        return logic_for_prompt_before_image(message)

    # if message['type'] == 'audio':
    #     path = download_file(message['audio'])
    #     text = retrieve_transcript_from_audio(path) # TBI
    # else:
    text = message['text']['body']

    if text.lower().strip() == 'cals':  # special keyword for calories tracking
        return retrieve_calories_from_image()

    operation_type = retrieve_message_type_from_message(text)
    print('operation_type', operation_type, len(operation_type))

    if operation_type == 'calendar':
        args = determine_calendar_event_inputs(text)
        args['color_id'] = 9 if args['type'] == 'reminder' and args['duration'] == 0.5 else 0
        del args['type']  # Faking the "reminders" in google cal, using a similar color, and default time
        create_google_calendar_event(**args)
        send_whatsapp_threaded('Event created successfully!')
        return ok
    elif operation_type == 'notion':
        arguments = determine_notion_page_inputs(text)
        add_new_page(**arguments)
        send_whatsapp_threaded('Notion page created successfully!')
        return ok
    elif operation_type == 'search':
        response = google_search_pipeline(text)
        send_whatsapp_threaded(response)
        return ok
    elif operation_type == 'image':
        return logic_for_prompt_before_image(message)
    else:
        response = simple_prompt_request(text + '. Respond in 10 to 15 words.')
        send_whatsapp_threaded(response)
        return ok
