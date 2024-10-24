# views.py
import requests
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decouple import config
from django.conf import settings
from .models import Payment
from .serializers import PaymentSerializer
from .redis_utils import redis_client , unlock_seats # Assuming you have a redis client setup
from .utils import unlock_db_seats
from decouple import config
class ProcessPaymentView(APIView):
    def post(self, request):
        token = request.data.get('token')
        order_id = request.data.get('order_id')
        order_service_url = f"{config('ORDER_SERVER_URL')}/details/"
        order_response = requests.post(
            order_service_url,
            json={
                'order_id': order_id,
                'token': token
                }
            )
        number_of_seats = order_response.json().get('number_of_seats')
            # Assuming lock key is named as `lock:{order_id}`
        ticket_class=order_response.json().get('ticket_class')
        user_id=order_response.json().get('user_id')
        train_id=order_response.json().get('train_id')
        train_service_url = f"{config('TRAIN_SERVER_URL')}/trains/{train_id}/ticket-class/{ticket_class}/"
        train_response = requests.get(
            train_service_url
        )
        price = train_response.json().get('price')
        lock_key = f"lock:{train_id}:{ticket_class}:{user_id}"
            # Check if the lock key still exists in Redis
        if redis_client.exists(lock_key):
            status = "successful"     
        else:
            unlock_db_seats(lock_key)
            status = "failed"

        unlock_seats(lock_key)
        payment = Payment.objects.create(
            order_id=order_id,
            status=status,
            amount=price*number_of_seats
        )
        payment.save()
        order_service_url = f"{config('ORDER_SERVER_URL')}/confirmOrder/"
        order_response = requests.post(
                order_service_url,
                json={
                    'order_id': order_id,
                    'token': token,
                    'payment_status': payment.status
                }
            )

        if order_response.status_code == 200:
            return Response({"payment":"Successful payment"}, status=status.HTTP_200_OK)
        return Response({"error": "Failed to update order server."}, status=status.HTTP_400_BAD_REQUEST)
