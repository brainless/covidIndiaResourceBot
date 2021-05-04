import aioredis

from utils.config import settings


redis = aioredis.from_url("redis://{}".format(settings.redis_host))


async def get_redis():
    return redis
