import json

from src.utils.redis import redis_client


def get_cache(key: str):
    data = redis_client.get(key)

    if data is None:
        return None

    return json.loads(data)


def set_cache(
    key: str,
    value,
    expire: int,
):
    redis_client.setex(
        key,
        expire,
        json.dumps(value),
    )


def delete_cache(key: str):
    redis_client.delete(key)


def delete_pattern(pattern: str):
    cursor = 0

    while True:
        cursor, keys = redis_client.scan(
            cursor=cursor,
            match=pattern,
            count=100,
        )

        if keys:
            redis_client.delete(*keys)

        if cursor == 0:
            break