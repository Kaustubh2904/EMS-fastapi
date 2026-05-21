import redis.asyncio as redis
from app.core.config import settings

class RedisCache:
    redis_client = None

cache = RedisCache()

async def connect_to_redis():
    cache.redis_client = await redis.from_url(settings.REDIS_URL, decode_responses=True)

async def close_redis_connection():
    if cache.redis_client:
        await cache.redis_client.close()

def get_redis():
    return cache.redis_client
