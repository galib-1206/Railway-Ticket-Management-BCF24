import requests
from decouple import config
from django.core.cache import cache
def unlock_db_seats(lock_key):
    # Assuming that keys are stored as "lock:{train_id}:{ticket_class}:{user_id}"
    key_parts = lock_key.split(":")
    if len(key_parts) == 4 and key_parts[0] == "lock":
        train_id, ticket_class = key_parts[1], key_parts[2]
        
        # Fetch the value of the lock key (number of seats)
        number_of_seats = cache.get(lock_key)
        number_of_seats = int(number_of_seats) if number_of_seats else 0  # Convert to int, default to 0 if None
        
        # Assuming the train server has an API to release tickets from the NDB.
        train_service_url = f"{config('TRAIN_SERVER_URL')}/trains/unlock-seats/"
        body ={"train_id": train_id,
                "ticket_class": ticket_class,
                "number_of_seats": number_of_seats }
        response = requests.post(train_service_url,json=body)
        return response.status_code