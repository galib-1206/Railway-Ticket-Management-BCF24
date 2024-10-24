from django.conf import settings
from .models import PendingRegistration
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserRegistrationSerializer, OTPVerificationSerializer, PasswordSetupSerializer
from django.contrib.auth.models import User
from rest_framework import status
from django.core.mail import send_mail
from rest_framework_simplejwt.views import TokenVerifyView
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.settings import api_settings
class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            email = serializer.validated_data['email']

            # Check if a PendingRegistration or User with this email already exists
            if User.objects.filter(email=email).exists():
                return Response({'detail': 'A user with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

            # Create a PendingRegistration entry
            pending_user = PendingRegistration.objects.create(username=username, email=email)
            pending_user.generate_otp()

            # Send OTP to email
            send_mail(
                'OTP Code',
                f'Your OTP for Ticket Management System is {pending_user.otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            return Response({'detail': 'User registration initiated. OTP sent to email.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class OTPVerificationView(APIView):
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']

            try:
                pending_user = PendingRegistration.objects.get(email=email)
                if pending_user.otp == otp:
                    if pending_user.is_otp_valid():
                        pending_user.otp_verified = True
                        pending_user.generate_reset_token()  # Generate a reset token
                        pending_user.save()

                        return Response({'detail': 'OTP verified successfully.','reset_token':pending_user.reset_token}, status=status.HTTP_200_OK)
                    else:
                        pending_user.delete()
                        return Response({'detail': 'OTP expired.'}, status=status.HTTP_400_BAD_REQUEST)
                pending_user.delete()
                return Response({'detail': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
            except PendingRegistration.DoesNotExist:
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
                pending_user = PendingRegistration.objects.get(email=email)
                if pending_user.is_reset_token_valid(reset_token):
                    user = User.objects.create_user(username=pending_user.username, email=email, password=password)
                    pending_user.delete()
                    user.save()
                    return Response({'detail': 'Password set successfully.'}, status=status.HTTP_200_OK)
                return Response({'detail': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class CustomTokenVerifyView(TokenVerifyView):
    def post(self, request, *args, **kwargs):
        token = request.data.get('token')

        # Verify the token as per default behavior
        serializer = self.get_serializer(data={'token': token})
        serializer.is_valid(raise_exception=True)

        try:
            # Decode the token to get user information
            token_backend = TokenBackend(algorithm=api_settings.ALGORITHM,signing_key=api_settings.SIGNING_KEY)
            decoded_token = token_backend.decode(token, verify=True)
            # Extract the user_id from the decoded token
            user_id = decoded_token.get('user_id')
            
            # Return success response with user_id included
            return Response({
                'user_id': user_id
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'detail': 'Token is invalid or expired'}, status=status.HTTP_401_UNAUTHORIZED)
    

