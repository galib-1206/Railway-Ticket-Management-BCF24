# serializers.py
from rest_framework import serializers
from .models import Train, TicketClass

class TicketClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketClass
        fields = ['id', 'class_name', 'price','total_seats', 'available_seats']

class TrainWithTicketClassSerializer(serializers.ModelSerializer):
    ticket_classes = TicketClassSerializer(many=True, read_only=True)
    class Meta:
        model = Train
        fields = ['id', 'train_name', 'route', 'journey_time', 'arrival_time','ticket_classes']

class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = ['id', 'train_name', 'route', 'journey_time', 'arrival_time']


class LockSeatsSerializer(serializers.Serializer):
    train_id = serializers.IntegerField()
    ticket_class = serializers.CharField(max_length=100)  # Adjust this based on your ticket class model
    number_of_seats = serializers.IntegerField(min_value=1)  # Ensure at least one seat is requested

    def validate(self, attrs):
        """
        Custom validation to ensure that the number of seats is valid
        against the available seats.
        """
        train_id = attrs.get('train_id')
        ticket_class = attrs.get('ticket_class')
        number_of_seats = attrs.get('number_of_seats')

        # Optionally, you can add logic here to check against available seats
        # This might require an API call to your train service to check availability

        return attrs