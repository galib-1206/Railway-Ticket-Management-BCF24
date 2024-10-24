import redis
from datetime import timedelta
from django.conf import settings

# Connect to Redis
redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
redis_client.config_set("notify-keyspace-events", "Ex")

