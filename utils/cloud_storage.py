import os

from google.cloud import storage

storage_client = storage.Client.from_service_account_json(
    os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'google-credentials.json'))
bucket_name = os.getenv('CLOUD_STORAGE_BUCKET_NAME')


def upload_image(path: str):
    print('upload_image:', path)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(path)
    blob.upload_from_filename(path, if_generation_match=0)
    return f'https://storage.googleapis.com/{bucket_name}/{path}'
