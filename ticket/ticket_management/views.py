# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Train, TicketClass
from .serializers import TrainSerializer, TrainWithTicketClassSerializer, LockSeatsSerializer

class TrainListView(APIView):
    def get(self, request):
        trains = Train.objects.all()
        serializer = TrainSerializer(trains, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TrainDetailView(APIView):
    def get(self, request, id):
        try:
            train = Train.objects.get(pk=id)
            serializer = TrainWithTicketClassSerializer(train)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Train.DoesNotExist:
            return Response({'detail': 'Train not found.'}, status=status.HTTP_404_NOT_FOUND)

class AvailableSeatsView(APIView):
    def get(self, request, train_id, ticket_class_id):
        try:
            # Get the train by train_id
            train = Train.objects.get(pk=train_id)
        except Train.DoesNotExist:
            return Response({'detail': 'Train not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Get the ticket class by ticket_class_id
            ticket_class = TicketClass.objects.get(pk=ticket_class_id, train=train)
        except TicketClass.DoesNotExist:
            return Response({'detail': 'Ticket class not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Return the number of available seats in the specified class
        return Response(
            {
                'train_id': train_id,
                'ticket_class_id': ticket_class_id,
                'available_seats': ticket_class.available_seats
            },
            status=status.HTTP_200_OK
        )
    
class LockSeatsView(APIView):
    def post(self, request, train_id, ticket_class_id):
        serializer = LockSeatsSerializer(data=request.data)
        if serializer.is_valid():
            number_of_seats = serializer.validated_data['number_of_seats']
            try:
                ticket_class = TicketClass.objects.get(pk=ticket_class_id, train_id=train_id)

                # Decrease available seats count
                if ticket_class.available_seats >= number_of_seats:
                    ticket_class.available_seats -= number_of_seats
                    ticket_class.save()
                    return Response({'message': 'Seats locked successfully.'}, status=status.HTTP_200_OK)

                return Response({'detail': 'Not enough available seats.'}, status=status.HTTP_400_BAD_REQUEST)
            except TicketClass.DoesNotExist:
                return Response({'detail': 'Ticket class not found.'}, status=status.HTTP_404_NOT_FOUND)
        print(serializer.error_messages)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UnlockSeatsView(APIView):
    def post(self, request):
        train_id = request.data.get('train_id')
        ticket_class = request.data.get('ticket_class')
        number_of_seats = request.data.get('number_of_seats')

        if not all([train_id, ticket_class, number_of_seats]):
            return Response({"error": "All fields (train_id, ticket_class, number_of_seats) are required."}, 
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            # Assuming TicketClass model has a method to unlock seats
            ticket_class_instance = TicketClass.objects.get(pk=ticket_class,train_id=train_id)
            ticket_class_instance.available_seats += number_of_seats  # Increase available seats
            ticket_class_instance.save()  # Save the updated instance

            return Response({"message": f"Unlocked {number_of_seats} seats for Train ID {train_id}, Class {ticket_class}."}, 
                            status=status.HTTP_200_OK)

        except TicketClass.DoesNotExist:
            return Response({"error": "Ticket class not found for the specified train."}, 
                            status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)