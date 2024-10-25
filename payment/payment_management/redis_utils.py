import redis
from datetime import timedelta
from django.conf import settings
from django.core.cache import cache

def unlock_seats(lock_key):
    cache.delete(lock_key)
