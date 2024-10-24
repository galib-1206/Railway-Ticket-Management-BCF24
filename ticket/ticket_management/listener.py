from .redis_utils import redis_client
import threading

from django.conf import settings

def redis_key_expiry_listener():
    pubsub = redis_client.pubsub()
    pubsub.psubscribe('__keyevent@0__:expired')  # Listen for expired events on Redis DB 0

    for message in pubsub.listen():
        if message['type'] == 'pmessage':
            expired_key = message['data'].decode('utf-8')
            process_expired_key(expired_key)

def process_expired_key(expired_key):
    from .models import TicketClass
    # Parse the key to extract train ID, ticket class, and user ID
    # Assuming keys are stored as "lock:{train_id}:{ticket_class}:{user_id}"
    key_parts = expired_key.split(":")
    number_of_seats = redis_client.hget(expired_key)
    if number_of_seats:
        number_of_seats = int(number_of_seats)
    if len(key_parts) == 4 and key_parts[0] == "lock":
        train_id = key_parts[1]
        ticket_class = key_parts[2]
        ticket_class = TicketClass.objects.get(pk=ticket_class, train_id=train_id)
        ticket_class.available_seats += number_of_seats
        ticket_class.save()
        print(f"Seats unlocked for Train: {train_id}, Class: {ticket_class}")

# Start the listener thread
def start_redis_listener():
    listener_thread = threading.Thread(target=redis_key_expiry_listener, daemon=True)
    listener_thread.start()


