from utils.cloud_storage import upload_image
from utils.gemini import *
from utils.redis_utils import get_generic_cache, set_generic_cache
from utils.whatsapp import send_whatsapp_threaded, download_file

redis_key = 'logic_for_prompt_after_image:most-recent-image'
ok = {'status': 'Ok'}


def retrieve_calories_from_image():
    # just testing, fails from 100 to 300 calories every time
    img_url = get_generic_cache(redis_key)
    if not img_url:
        send_whatsapp_threaded('Please send an image of the food item.')
        return ok
    # too personalized, but ish
    response: str = analyze_image(img_url, '''
    Estimate the amount of calories in the food in the picture, also estimate the macros.
    If you see chicken breast, the user always eats 250g.
    If you see a sandwich, the user eats 40g of cheese, 2 slices of ham (21g each), and white bread (18g carbs, 3g protein, 0.4g fat per slice).
    If you see rice, the user puts on hist plate always 300g.
    If you see granola and yogurt, the user eats 80g of granola and 150g of greek yogurt.
    Output a JSON in the following format:
    {"carbs": 10, "protein": 10, "fats": 10, "calories": 160}
    Do not output any context or anything more than the JSON.'''.replace('    ', ''))
    send_whatsapp_threaded(response)
    return ok


def logic_for_prompt_before_image(message: dict):
    if message['type'] == 'image':
        path = download_file(message['image'])
        if not path:
            return ok
        img_url = upload_image(path)
        if not img_url:
            return ok

        set_generic_cache(redis_key, img_url, ttl=60 * 10)
    elif message['type'] == 'text':
        prompt = message['text']['body']
        if not prompt:
            return ok

        img_url = get_generic_cache(redis_key)
        response: str = analyze_image(img_url, prompt + '. Respond in 10 to 15 words.')
        # TODO: keep thread id? to be able to send a message to the same thread
        send_whatsapp_threaded(response)
    return ok
