import os

import requests
from notion_client import Client

# Your Notion credentials
client = Client(auth=os.getenv('NOTION_INTEGRATION_SECRET'))
db_id = os.getenv('NOTION_DATABASE_ID')


def add_new_page(title: str, category: str, content: str):
    data = {
        "parent": {"database_id": 'abff2f35712b49a28379f595be2706e4'},
        "properties": {
            "Title": {"title": [{"text": {"content": title}}]},
            "Category": {"select": {"name": category}},
            "Content": {"rich_text": [{"text": {"content": content}}]}
        }
    }
    requests.post('https://api.notion.com/v1/pages', json=data, headers={
        'Authorization': f'Bearer {os.getenv("NOTION_INTEGRATION_SECRET")}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Notion-Version': '2022-06-28'
    })
    print(f"New Notion page created with title: {title}")
    # TODO: write any detail to this page, or related terms (suggested by Gemini)


# TODO: implement function to retrieve pages where are about X, and return in simple message what have been told
# add_new_page('Test', 'Personal', 'This is a test page')
