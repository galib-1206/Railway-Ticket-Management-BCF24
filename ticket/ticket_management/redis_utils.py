import redis
from datetime import timedelta
from django.conf import settings
from django.core.cache import cache
from django_redis import get_redis_connection
# Connect to Redis
redis_client = get_redis_connection("default")
# redis_client.config_set("notify-keyspace-events", "Ex")

