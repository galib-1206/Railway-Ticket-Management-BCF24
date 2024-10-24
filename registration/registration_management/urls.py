# accounts/urls.py
from django.urls import path
from .views import UserRegistrationView, OTPVerificationView, PasswordSetupView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('verify-otp/', OTPVerificationView.as_view(), name='verify-otp'),
    path('set-password/', PasswordSetupView.as_view(), name='set-password'),
]
