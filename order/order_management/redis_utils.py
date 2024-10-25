import redis
from datetime import timedelta
from django.conf import settings
from django.core.cache import cache

def lock_seats(user_id, train_id, ticket_class, number_of_seats):
    lock_key = f"lock:{train_id}:{ticket_class}:{user_id}"
    # Try to set the lock with a timeout of 2 minutes
    if cache.set(lock_key, number_of_seats, ex=timedelta(minutes=2), nx=True):
        cache.set(f"backup:{lock_key}", number_of_seats, ex=timedelta(minutes=3))
        return True
    return False
