# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import timedelta
import random
from django.db import models
from django.utils import timezone
import random

class PendingRegistration(models.Model):
    email = models.EmailField()
    username = models.CharField(max_length=150)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_verified = models.BooleanField(default=False)
    reset_token = models.CharField(max_length=64, blank=True, null=True)
    reset_token_expiration = models.DateTimeField(null=True, blank=True)
    otp_expiration = models.DateTimeField(null=True, blank=True)
    
    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))  # Generate a 6-digit OTP
        self.otp_verified = False
        self.otp_expiration = timezone.now() + timedelta(minutes=3)  # Set expiration for 5 minutes
        self.save()

    def is_otp_valid(self):
        if timezone.now() < self.otp_expiration: 
            return True
        return False

    def generate_reset_token(self):
        self.reset_token = uuid.uuid4().hex
        self.reset_token_expiration = timezone.now() + timedelta(minutes=10)
        self.save()

    def is_reset_token_valid(self, token):
        if self.reset_token == token and self.reset_token_expiration and timezone.now() < self.reset_token_expiration:
            return True
        return False

    def __str__(self):
        return self.user.username
    