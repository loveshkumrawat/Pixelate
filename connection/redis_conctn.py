import redis
from supporting import env

redis_server = redis.Redis(
    host=env.REDIS_HOST,
    port=env.REDIS_PORT,
    decode_responses=True
)