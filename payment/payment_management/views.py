# views.py
import requests
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.conf import settings
from .models import Payment
from .serializers import PaymentSerializer
from .redis_utils import redis_client , unlock_seats # Assuming you have a redis client setup
from .utils import unlock_db_seats

class ProcessPaymentView(APIView):
    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        token = request.data.token
        if serializer.is_valid():
            order_id = serializer.validated_data['order_id']
            payment_id = serializer.validated_data['payment_id']
            amount = serializer.validated_data['amount']
            order_service_url = f"{settings.ORDER_SERVER_URL}/order/details/"
            order_response = requests.post(
                order_service_url,
                json={
                    'order_id': order_id,
                    'token': token
                }
            )
            # Assuming lock key is named as `lock:{order_id}`
            ticket_class=order_response.json().get('ticket_class')
            user_id=order_response.json().get('user_id')
            train_id=order_response.json().get('train_id')
            lock_key = f"lock:{train_id}:{ticket_class}:{user_id}"

            # Check if the lock key still exists in Redis
            if redis_client.exists(lock_key):
                # Lock is still active; update payment status to "successful"
                serializer.validated_data['status'] = "successful"
                
            else:
                # Lock is expired; update payment status to "failed"
                unlock_db_seats(lock_key)
                serializer.validated_data['status'] = "failed"

            unlock_seats(lock_key)

            # Save the payment data
            payment = serializer.save()

            # Send payment status to the Order Server API
            order_service_url = f"{settings.ORDER_SERVER_URL}/order/confirmOrders/"
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
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
