# accounts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .models import Profile
from .serializers import UserRegistrationSerializer, OTPVerificationSerializer, PasswordSetupSerializer
import random

class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            email = serializer.validated_data['email']

            # Check if a user with this email already exists
            if User.objects.filter(email=email).exists():
                return Response({'detail': 'A user with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

            # Create the user without setting a password
            user = User.objects.create(username=username, email=email)
            otp = random.randint(100000, 999999)  # Generate a 6-digit OTP

            # Send OTP to email
            send_mail(
                'Your OTP Code',
                f'Your OTP is {otp}',
                'admin@myapp.com',
                [email],
                fail_silently=False,
            )

            # Save OTP to user profile
            profile = user.profile
            profile.otp = otp
            profile.otp_verified = False
            profile.save()

            return Response({'detail': 'User registered successfully. OTP sent to email.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# accounts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .models import Profile
from .serializers import UserRegistrationSerializer, OTPVerificationSerializer, PasswordSetupSerializer
import random

class OTPVerificationView(APIView):
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']

            try:
                user = User.objects.get(email=email)
                if user.profile.otp == otp:
                    user.profile.otp_verified = True
                    user.profile.generate_reset_token()  # Generate a reset token
                    user.profile.save()

                    # Send token via email
                    send_mail(
                        'Your Password Reset Token',
                        f'Your reset token is {user.profile.reset_token}',
                        'admin@myapp.com',
                        [email],
                        fail_silently=False,
                    )

                    return Response({'detail': 'OTP verified successfully. Reset token sent to email.'}, status=status.HTTP_200_OK)
                return Response({'detail': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# accounts/views.py (only modified section)
class PasswordSetupView(APIView):
    def post(self, request):
        serializer = PasswordSetupSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            # Extract reset_token from headers
            reset_token = request.headers.get('X-Reset-Token')  # Custom header name
            
            if not reset_token:
                return Response({'detail': 'Reset token missing in headers.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(email=email)
                if user.profile.is_reset_token_valid(reset_token):
                    user.set_password(password)
                    user.profile.reset_token = None  # Invalidate the token after use
                    user.profile.reset_token_expiration = None
                    user.save()
                    user.profile.save()
                    return Response({'detail': 'Password set successfully.'}, status=status.HTTP_200_OK)
                return Response({'detail': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
