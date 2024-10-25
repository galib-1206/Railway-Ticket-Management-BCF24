from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class LockSeatsSerializer(serializers.Serializer):
    train_id = serializers.IntegerField()
    ticket_class = serializers.CharField(max_length=50)
    number_of_seats = serializers.IntegerField()

class ConfirmOrderSerializer(serializers.Serializer):
    train_id = serializers.IntegerField()
    ticket_class = serializers.CharField(max_length=50)
    number_of_seats = serializers.IntegerField()
