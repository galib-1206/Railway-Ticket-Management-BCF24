from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LockSeatsSerializer, ConfirmOrderSerializer, OrderSerializer
from .models import Order
from .redis_utils import lock_seats
import requests
from decouple import config
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LockSeatsSerializer
from django.conf import settings  # Ensure you're using Django's settings
from django.core.cache import cache
class LockSeatsView(APIView):
    def post(self, request):
        serializer = LockSeatsSerializer(data=request.data)
        
        # Verify the token with the auth server
        auth_url = f"{config('REGISTRATION_SERVER_URL')}/verify/"
        body = {
            'token': request.data.get('token')
        }
        auth_response = requests.post(auth_url, json=body)
        
        if auth_response.status_code != 200:
            return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        user_data = auth_response.json()

        if serializer.is_valid():
            user_id = user_data.get('user_id')  # Assuming the user ID is set by the middleware
            train_id = serializer.validated_data['train_id']
            ticket_class = serializer.validated_data['ticket_class']
            number_of_seats = serializer.validated_data['number_of_seats']

            # Call train service to check available seats
            train_service_url = f"{config('TRAIN_SERVER_URL')}/trains/{train_id}/ticket-class/{ticket_class}/"
            response = requests.get(train_service_url)
            
            if response.status_code == 200:
                available_seats = response.json().get('available_seats')
                 
                if (available_seats >= number_of_seats):
                    # Call Redis function to lock seats
                    if lock_seats(user_id, train_id, ticket_class, number_of_seats):
                        # Notify train service to update the seat availability
                        update_url = f"{config('TRAIN_SERVER_URL')}/trains/{train_id}/ticket-class/{ticket_class}/lock/"
                        update_response = requests.post(update_url, json={'number_of_seats': number_of_seats,'train_id':train_id,'ticket_class':ticket_class})
                        if update_response.status_code == 200:
                            return Response({'message': 'Seats locked successfully.'}, status=status.HTTP_200_OK)
                        
                        return Response({'message': 'Unable to lock seats in the train service.'}, status=status.HTTP_400_BAD_REQUEST)
                    return Response({'message': 'Already locked.'}, status=status.HTTP_400_BAD_REQUEST)
                return Response({'message': 'Insufficient seats available.'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GiveOrderView(APIView):
    def post(self, request):
        serializer = ConfirmOrderSerializer(data=request.data)
        auth_url = f"{config('REGISTRATION_SERVER_URL')}/verify/"  # Replace with your API URL
        body = {
            'token': request.data.get('token')
        }
        auth_response = requests.post(auth_url, json=body)
        
        if auth_response.status_code != 200:
            return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        user_data = auth_response.json()
        if serializer.is_valid():
            user_id = user_data.get('user_id') # Assuming the user ID is set by the middleware
            train_id = serializer.validated_data['train_id']
            ticket_class = serializer.validated_data['ticket_class']
            number_of_seats = serializer.validated_data['number_of_seats']

            # Check if the seats are still locked for this user
            lock_key = f"lock:{train_id}:{ticket_class}:{user_id}"
            if cache.exists(lock_key):
                #cache.expire(lock_key, 300)
                order = Order.objects.create(
                    user_id=user_id,
                    train_id=train_id,
                    ticket_class=ticket_class,
                    number_of_seats=number_of_seats,
                    status="PENDING"
                    )
                return Response({'status': order.status, 'order_id': order.id}, status=status.HTTP_200_OK)
            return Response({'message': 'Lock expired or not found.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class OrderDetailView(APIView):
    def post(self, request):
        # Extract order_id and token from the request body
        order_id = request.data.get('order_id')
        token = request.data.get('token')

        if not order_id or not token:
            return Response({'detail': 'Order ID and token are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Verify token with the auth server
        auth_url = f"{config('REGISTRATION_SERVER_URL')}/verify/"  # Replace with your API URL
        auth_response = requests.post(auth_url, json={'token': token})

        if auth_response.status_code != 200:
            return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # Get user_id from the verified token response
        user_id = auth_response.json().get('user_id')
        if not user_id:
            return Response({'detail': 'User ID not found in token.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            # Get the order by order_id
            order = Order.objects.get(id=order_id)

            # Check if the user_id matches
            if order.user_id != user_id:
                return Response({'detail': 'User ID does not match with the order.'}, status=status.HTTP_403_FORBIDDEN)

            # Serialize the order if everything is valid
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

class ConfirmedOrderView(APIView):
    def post(self, request):
        # Extract order_id, token, and payment_status from the request body
        order_id = request.data.get('order_id')
        token = request.data.get('token')
        payment_status = request.data.get('payment_status')

        if not order_id or not token:
            return Response({'detail': 'Order ID and token are required.'}, status=status.HTTP_400_BAD_REQUEST)
        order = Order.objects.get(id=order_id)
        if payment_status == 'success':
            order.status = 'CANCELLED'
            order.save()
            return Response({'detail': 'Payment status must be true to confirm the order.'}, status=status.HTTP_400_BAD_REQUEST)

        # Verify token with the auth server
        auth_url = f"{config('REGISTRATION_SERVER_URL')}/verify/"  # Replace with your API URL
        auth_response = requests.post(auth_url, json={'token': token})

        if auth_response.status_code != 200:
            return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # Get user_id from the verified token response
        user_id = auth_response.json().get('user_id')
        if not user_id:
            return Response({'detail': 'User ID not found in token.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            # Get the order by order_id
            

            # Check if the user_id matches
            if order.user_id != user_id:
                return Response({'detail': 'User ID does not match with the order.'}, status=status.HTTP_403_FORBIDDEN)

            # Set the order status to confirmed if payment status is true
            order.status = 'CONFIRMED'
            order.save()

            return Response({'message': 'Order confirmed successfully.'}, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)