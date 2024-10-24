# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import datetime, timedelta

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    account_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    phone = models.CharField(max_length=15, blank=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_verified = models.BooleanField(default=False)
    reset_token = models.CharField(max_length=64, blank=True, null=True)
    reset_token_expiration = models.DateTimeField(null=True, blank=True)

    def generate_reset_token(self):
        # Generate a new token and set an expiration time (e.g., 10 minutes from now)
        self.reset_token = uuid.uuid4().hex
        self.reset_token_expiration = datetime.now() + timedelta(minutes=10)
        self.save()

    def is_reset_token_valid(self, token):
        if self.reset_token == token and self.reset_token_expiration and datetime.now() < self.reset_token_expiration:
            return True
        return False

    def __str__(self):
        return self.user.username
