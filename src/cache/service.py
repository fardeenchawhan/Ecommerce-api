import json

from fastapi.encoders import jsonable_encoder
from redis.exceptions import RedisError

from src.utils.redis import redis_client


def get_cache(key: str):
    try:
        data = redis_client.get(key)

        if data is None:
            return None

        return json.loads(data)

    except RedisError:
        return None


def set_cache(
    key: str,
    value,
    expire: int,
):
    try:
        redis_client.setex(
            key,
            expire,
            json.dumps(jsonable_encoder(value)),
        )
    except RedisError:
        pass


def delete_cache(key: str):
    try:
        redis_client.delete(key)
    except RedisError:
        pass


def delete_pattern(pattern: str):
    try:
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

    except RedisError:
        pass