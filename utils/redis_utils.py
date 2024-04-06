import os
import json
import base64
import redis

r = redis.Redis(
    host=os.getenv('REDIS_DB_HOST', 'localhost'),
    port=int(os.getenv('REDIS_DB_PORT', '6378')),
    username='default',
    password=os.getenv('REDIS_DB_PASSWORD', ''),
    health_check_interval=30
)


def try_catch_decorator(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f'Error calling {func.__name__}', e)
            return None

    return wrapper


# ------------ Place ID Caching ------------
@try_catch_decorator
def get_generic_cache(path: str):
    key = base64.b64encode(f'{path}'.encode('utf-8'))
    key = key.decode('utf-8')

    data = r.get(f'josancamon:rayban-meta-glasses-api:{key}')
    return json.loads(data) if data else None


@try_catch_decorator
def set_generic_cache(path: str, data: dict, ttl: int = None):
    key = base64.b64encode(f'{path}'.encode('utf-8'))
    key = key.decode('utf-8')

    r.set(f'josancamon:rayban-meta-glasses-api:{key}', json.dumps(data, default=str))
    if ttl:
        r.expire(f'josancamon:rayban-meta-glasses-api:{key}', ttl)


@try_catch_decorator
def delete_generic_cache(path: str):
    key = base64.b64encode(f'{path}'.encode('utf-8'))
    key = key.decode('utf-8')
    r.delete(f'josancamon:rayban-meta-glasses-api{key}')

# Code to connect to Redis from local machine from GCP
# gcloud compute ssh redis-proxy --project=$project-id --zone us-central1-a -- -N -L 6379:$redis-private-ip:6379
