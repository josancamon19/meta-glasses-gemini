import os

import google.ai.generativelanguage as glm
import google.generativeai as genai
import requests
from PIL import Image
from datetime import datetime

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

retrieve_message_type_from_message_description = '''
Based on the message type, execute some different requests to APIs or other tools. 
- calendar: types are related to anything with scheduling, events, reminders, etc. 
- image: types are related to anything with images, pictures, what's the user looking at, what's in front of the user, etc.
- notion: anything related to storing a note, save an idea, notion, etc. 
- search: types are related to anything with searching, finding, looking for, and it's about a recent event, or news etc.
- other: types are related to anything else.

Make sure to always return the message type, or default to `other` even if it doesn't match any of the types.
'''.replace('    ', '')

determine_calendar_event_inputs_description = f'''
Based on the message, create an event using the Google Calendar API. 
- title: The title of the event
- description: The description of the event, if any, if not return an empty string
- date: The date of the event in the format `YYYY-MM-DD`. Today is {datetime.now().strftime('%Y-%m-%d')}, so if the user says "tomorrow", or in 1 week, etc, make sure to calculate the correct date.
- time: The time of the event in the format `HH:MM`
- duration: The duration of the event in hours
- type: The type of message the user sent, default to `event`

Make sure to return all the required inputs for the event creation.
'''.replace('    ', '')

determine_notion_page_inputs_description = f'''Based on the message, create a new page in your Notion database. 
- title: The title of the page
- category: The category of the page, default to `Note`
- content: The content of the message in the user words (without more detail, just in user words)

Make sure to return all the required inputs for the page creation.
'''.replace('    ', '')


def simple_prompt_request(message: str):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(message)
    return response.text.strip()


def generate_google_search_query(user_input: str):
    return simple_prompt_request(f'''You are a Google Search Expert. You task is to convert unstructured user inputs to optimized Google search queries. Example: USER INPUT: 'Best places to visit in Colombia?' OPTIMIZED Google Search Query: 'Top 10 Colombia tourist destinations'.
    Convert the following user query into a optimized Google Search query: "{user_input}"''')


def retrieve_scraped_data_short_answer(news_content: str, user_query: str):
    return simple_prompt_request(f'''You are a helpful assistant, You take the user query and the text from scraped data of articles/news/pages, and return a short condenseated answer to the user query based on the scraped data, use 10 to 15 words.
    Context: {news_content}\nUser Query: {user_query}''')


def _get_func_arg_parameter(description: str, param_type: str = 'string', enum_options: list = None):
    if enum_options:
        return glm.Schema(
            type=glm.Type.STRING,
            enum=enum_options,
            description=description
        )
    return glm.Schema(
        type=glm.Type.STRING if param_type == 'string' else glm.Type.NUMBER,
        description=description
    )


def _get_tool(tool_name: str, description: str, parameters: dict, required: list = None):
    if not required:
        required = list(parameters.keys())
    return glm.Tool(
        function_declarations=[
            glm.FunctionDeclaration(
                name=tool_name,
                description=description,
                parameters=glm.Schema(
                    type=glm.Type.OBJECT,
                    properties=parameters,
                    required=required
                )
            )
        ])


def analyze_image(img_url: str, prompt: str):
    image_path = 'media/' + img_url.split('/')[-1]
    download_image = requests.get(img_url)
    print('Downloaded image', download_image.status_code, image_path)
    with open(image_path, 'wb') as f:
        f.write(download_image.content)

    img = Image.open(image_path)
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content([prompt, img], stream=False)
    return response.text.strip()


def retrieve_message_type_from_message(message: str):
    print('retrieve_message_type_from_message', message)
    if not message:
        return ''

    tool = _get_tool(
        'execute_based_on_message_type',
        retrieve_message_type_from_message_description,
        {"message_type": _get_func_arg_parameter(
            'The type of message the user sent', 'string',
            ["calendar", "image", "notion", "search", "other"])})
    model = genai.GenerativeModel(model_name='gemini-1.0-pro', tools=[tool])
    chat = model.start_chat(enable_automatic_function_calling=True)
    response = chat.send_message(message)
    fc = response.candidates[0].content.parts[0].function_call
    assert fc.name == 'execute_based_on_message_type'
    print('retrieve_message_type_from_message response:', fc.args['message_type'])
    return fc.args['message_type']


def determine_calendar_event_inputs(message: str):
    tool = _get_tool('determine_calendar_event_inputs', determine_calendar_event_inputs_description, {
        "title": _get_func_arg_parameter('The title of the event'),
        "description": _get_func_arg_parameter('The description of the event, if any, if not return an empty string'),
        "date": _get_func_arg_parameter('The date of the event in the format `YYYY-MM-DD`'),
        "time": _get_func_arg_parameter('The time of the event in the format `HH:MM`'),
        "duration": _get_func_arg_parameter(
            'The duration of the event in hours, default is 1 hour, but if the type is a `reminder`, default to 0.5 hours.',
            'integer'),
        "type": _get_func_arg_parameter('The type of message the user sent, default to `event`', 'string',
                                        ["reminder", "event", "time-block"])
    })

    model = genai.GenerativeModel(model_name='gemini-1.0-pro', tools=[tool])
    chat = model.start_chat(enable_automatic_function_calling=True)
    response = chat.send_message(message)
    fc = response.candidates[0].content.parts[0].function_call
    print(fc)
    assert fc.name == 'determine_calendar_event_inputs'
    return {
        'title': fc.args['title'],
        'description': fc.args['description'],
        'date': fc.args['date'],
        'time': fc.args['time'],
        'duration': fc.args.get('duration', 1),
        'type': fc.args['type']
    }


def determine_notion_page_inputs(message: str):
    tool = _get_tool('determine_notion_page_inputs', determine_notion_page_inputs_description, {
        "title": _get_func_arg_parameter('The title of the page'),
        "category": _get_func_arg_parameter(
            '''
            The category of the page, default to `Note`. 
            If it is a business idea, or something about entrepreneurship, or about making money, use `Idea`.
            If it is about work, or a project, use `Work`.
            If it is about personal stuff, or something about the user, use `Personal`, either money on a personal level, relationships, etc.
            Else, use `Note`.
            ''',
            enum_options=["Note", "Idea", "Work", "Personal"]),
        "content": _get_func_arg_parameter('The content of the message in the user words (more detail)')
    })
    model = genai.GenerativeModel(model_name='gemini-1.0-pro', tools=[tool])
    chat = model.start_chat(enable_automatic_function_calling=True)
    response = chat.send_message(message)
    fc = response.candidates[0].content.parts[0].function_call
    assert fc.name == 'determine_notion_page_inputs'
    return {
        'title': fc.args['title'],
        'category': fc.args['category'],
        'content': fc.args['content']
    }
