

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
from .redis_utils import redis_client, unlock_seats  # Assuming you have a redis client setup
from .utils import unlock_db_seats
from django.core.cache import cache
class ProcessPaymentView(APIView):
    def post(self, request):
        try:
            # Extract data from request
            token = request.data.get('token')
            order_id = request.data.get('order_id')
            if not (token and order_id):
                return Response({"error": "Token and Order ID are required."}, status=status.HTTP_400_BAD_REQUEST)

            # Step 1: Get order details from Order Service
            try:
                order_service_url = f"{config('ORDER_SERVER_URL')}/details/"
                order_response = requests.post(
                    order_service_url,
                    json={'order_id': order_id, 'token': token}
                )
                order_response.raise_for_status()  # Raises an HTTPError if the status is 4xx/5xx

                order_data = order_response.json()
                number_of_seats = order_data.get('number_of_seats')
                ticket_class = order_data.get('ticket_class')
                user_id = order_data.get('user_id')
                train_id = order_data.get('train_id')

                if not all([number_of_seats, ticket_class, user_id, train_id]):
                    return Response({"error": "Invalid order data received from Order Service."}, status=status.HTTP_400_BAD_REQUEST)
            except requests.exceptions.RequestException as e:
                return Response({"error": "Failed to fetch order details from Order Service.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Step 2: Get ticket class price from Train Service
            try:
                train_service_url = f"{config('TRAIN_SERVER_URL')}/trains/{train_id}/ticket-class/{ticket_class}/"
                train_response = requests.get(train_service_url)
                train_response.raise_for_status()

                price = train_response.json().get('price')
                if price is None:
                    return Response({"error": "Failed to retrieve ticket price from Train Service."}, status=status.HTTP_400_BAD_REQUEST)
            except requests.exceptions.RequestException as e:
                return Response({"error": "Failed to fetch ticket class details from Train Service.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Step 3: Check lock key existence in Redis
            lock_key = f"lock:{train_id}:{ticket_class}:{user_id}"
            if cache.exists(lock_key):
                payment_status = "successful"
            else:
                unlock_db_seats(lock_key)  # Unlock seats in the DB if Redis lock expired
                payment_status = "failed"

            # Unlock Redis lock
            unlock_seats(lock_key)

            # Step 4: Create Payment record
            try:
                payment = Payment.objects.create(
                    order_id=order_id,
                    payment_id=order_id + token,  # Assuming unique ID logic here, adjust as needed
                    status=payment_status,
                    amount=price * number_of_seats
                )
            except Exception as e:
                return Response({"error": "Failed to create payment record.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Step 5: Send payment status to Order Service
            try:
                confirm_order_url = f"{config('ORDER_SERVER_URL')}/confirmOrder/"
                order_confirm_response = requests.post(
                    confirm_order_url,
                    json={'order_id': order_id, 'token': token, 'payment_status': payment.status}
                )
                order_confirm_response.raise_for_status()
            except requests.exceptions.RequestException as e:
                return Response({"error": "Failed to confirm payment with Order Service.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Return success response
            return Response({"payment": "Successful payment"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": "An unexpected error occurred.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

