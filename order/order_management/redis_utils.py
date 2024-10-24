import redis
from datetime import timedelta
from django.conf import settings

# Connect to Redis
redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

def lock_seats(user_id, train_id, ticket_class, number_of_seats):
    lock_key = f"lock:{train_id}:{ticket_class}:{user_id}"
    # Try to set the lock with a timeout of 2 minutes
    if redis_client.set(lock_key, number_of_seats, ex=timedelta(minutes=2), nx=True):
        redis_client.hset(lock_key, number_of_seats)
        return True
    return False
