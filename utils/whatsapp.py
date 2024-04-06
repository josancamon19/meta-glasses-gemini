import os

import requests

headers = {
    'Authorization': f'Bearer {os.getenv("WHATSAPP_AUTH_TOKEN")}',
    'Content-Type': 'application/json',
}


def send_whatsapp_message(text: str):
    print('send_whatsapp_message', text)
    json_data = {
        'messaging_product': 'whatsapp',
        'to': os.getenv('WHATSAPP_PHONE_NUMBER'),
        'type': 'text',
        'text': {'body': text}
    }
    url = 'https://graph.facebook.com/v18.0/257413590792295/messages'
    response = requests.post(url, headers=headers, json=json_data)
    print('send_whatsapp_message:', response.json())


def download_file(file_data):
    print('download_image', file_data)
    res = requests.get(f'https://graph.facebook.com/v19.0/{file_data["id"]}/', headers=headers)
    print(res.json())
    url = res.json()['url']
    response = requests.get(url, headers=headers)
    if not os.path.exists('media/'):
        os.makedirs('media/')

    file_format = 'ogg' if 'audio' in file_data['mime_type'] else 'jpg'
    if response.status_code == 200:
        with open(f'media/{file_data["id"]}.{file_format}', "wb") as f:
            f.write(response.content)
        print("Media file download successful")
        return f'media/{file_data["id"]}.{file_format}'
    else:
        print("Download failed. Status code:", response.status_code)


def send_whatsapp_threaded(message: str):
    # call send_message for every 10 words, glasses read from whatsapp at most 15 words, otherwise say "Long message"
    send_whatsapp_message(message)
    # words = message.split()
    # for i in range(0, len(words), 10):
    #     # print('Sending', ' '.join(words[i:i + 10]))
    #     send_message(' '.join(words[i:i + 10]))
    #     time.sleep(10)
