import os

from notion_client import Client

# Your Notion credentials
DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
client = Client(auth=os.getenv('NOTION_INTEGRATION_SECRET'))


def add_new_page(title, category, content):
    new_page = client.pages.create(
        parent={"type": "database_id", "database_id": DATABASE_ID},
        properties={
            "Title": {"title": [{"text": {"content": title}}]},
            "Category": {"select": {"name": category}},
            "Content": {"rich_text": [{"text": {"content": content}}]}
        }
    )
    print(f"New Notion page created with title: {title}")
    # TODO: write any detail to this page, or related terms (suggested by Gemini)

# TODO: implement function to retrieve pages where are about X, and return in simple message what have been told
