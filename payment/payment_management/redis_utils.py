import redis
from datetime import timedelta
from django.conf import settings

# Connect to Redis
redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

def unlock_seats(user_id, train_id, ticket_class):
    lock_key = f"lock:{train_id}:{ticket_class}:{user_id}"
    redis_client.delete(lock_key)
