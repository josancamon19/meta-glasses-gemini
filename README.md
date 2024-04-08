# Meta Rayban Glasses + Gemini Integration Project

This project integrates the Meta Rayban Glasses with a WhatsApp bot, leveraging the power of Google Gemini, Redis for
data management, Notion for note-taking, and Google Calendar for event and reminder management. This README guides you
through setting up the project environment, including necessary configurations and API integrations.

## Getting Started

### Prerequisites

- Python 3.x
- pip for Python package installation

### Installation

1. Clone this repository to your local machine.
2. Navigate to the project directory.
3. Install the required Python packages:

    ```sh
    pip install -r requirements.txt
    ```

### Environment Variables

You need to set the following environment variables in a `.env` file within the project directory:

```dotenv
WHATSAPP_AUTH_TOKEN=
WHATSAPP_PHONE_NUMBER=
WHATSAPP_WEBHOOK_VERIFICATION_TOKEN=
REDIS_DB_HOST=
REDIS_DB_PORT=
REDIS_DB_PASSWORD=
GEMINI_API_KEY=
CLOUD_STORAGE_BUCKET_NAME=
NOTION_INTEGRATION_SECRET=
NOTION_DATABASE_ID=
SERPER_DEV_API_KEY=
CRAWLBASE_API_KEY=
```

- `WHATSAPP_AUTH_TOKEN`: Create an app at [Meta for Developers](https://developers.facebook.com/) and retrieve the
  WhatsApp authentication token.
- `WHATSAPP_PHONE_NUMBER`: The phone number associated with your WhatsApp API.
- `WHATSAPP_WEBHOOK_VERIFICATION_TOKEN`: Set a verification token of your choice and use it in the Meta for Developers
  dashboard to verify the webhook.
- `REDIS_DB_HOST`, `REDIS_DB_PORT`, `REDIS_DB_PASSWORD`: Credentials for your Redis database. This project uses Redis
  for managing data, including storing images for analysis.
- `GEMINI_API_KEY`: Obtain this from the Google Gemini API for image analysis and AI capabilities.
- `CLOUD_STORAGE_BUCKET_NAME`: The name of your Google Cloud Storage bucket for storing images and data.
- `NOTION_INTEGRATION_SECRET`, `NOTION_DATABASE_ID`: Create a Notion integration and a database with fields (Title,
  Category, Content, Created At, Completed). Share the database with the integration.
- `SERPER_DEV_API_KEY`, `CRAWLBASE_API_KEY`: Obtain these API keys from the respective websites to enable advanced
  search and data retrieval functionalities.

### Additional Configuration

- **Google Cloud Platform Credentials**: Place your `google-credentials.json` file in the project root. This file should
  contain credentials for your GCP project.
- **Google OAuth Token**: Ensure you have a `credentials.json` file for OAuth to enable Google Calendar integrations.
  Follow the Google Calendar API documentation to obtain this token.