# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import PendingRegistration

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PendingRegistration
        fields = ['username', 'email']

class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)


class PasswordSetupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

