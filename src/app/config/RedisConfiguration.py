import redis
from redis import Redis

from .Configuration import Configuration


def get_redis_client(config: Configuration) -> Redis:
    return redis.Redis(host=config.redis_host, port=config.redis_port, decode_responses=True)

