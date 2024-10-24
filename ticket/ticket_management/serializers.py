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
        fields = ['id', 'train_name', 'route', 'journey_time', 'arrival_time', 'total_seats', 'available_seats','ticket_classes']

class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = ['id', 'train_name', 'route', 'journey_time', 'arrival_time', 'total_seats', 'available_seats']
