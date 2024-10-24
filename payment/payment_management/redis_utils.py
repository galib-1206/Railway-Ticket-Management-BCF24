import redis
from datetime import timedelta
from django.conf import settings

# Connect to Redis
redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

def unlock_seats(lock_key):
    redis_client.delete(lock_key)
