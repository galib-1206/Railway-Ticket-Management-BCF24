from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.mail import send_mail
from unittest.mock import patch
from .models import PendingRegistration
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
class UserRegistrationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.verify_otp_url = reverse('verify-otp')
        self.set_password_url = reverse('set-password')

    @patch('django.core.mail.send_mail')
    def test_user_registration_success(self, mock_send_mail):
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PendingRegistration.objects.count(), 1)
        self.assertTrue(mock_send_mail.called)

    def test_user_registration_email_exists(self):
        PendingRegistration.objects.create(username='testuser', email='testuser@example.com')
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'A user with this email already exists.')

class OTPVerificationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.verify_otp_url = reverse('verify-otp')
        self.set_password_url = reverse('set-password')

        # Register a user first
        self.client.post(self.register_url, {'username': 'testuser', 'email': 'testuser@example.com'}, format='json')
        self.pending_user = PendingRegistration.objects.first()
        self.pending_user.generate_otp()  # Make sure OTP is generated

    def test_otp_verification_success(self):
        data = {
            'email': self.pending_user.email,
            'otp': self.pending_user.otp
        }
        response = self.client.post(self.verify_otp_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.pending_user.otp_verified)

    def test_otp_verification_expired_otp(self):
        self.pending_user.otp_expiration = timezone.now() - timedelta(minutes=5)
        self.pending_user.save()

        data = {
            'email': self.pending_user.email,
            'otp': self.pending_user.otp
        }
        response = self.client.post(self.verify_otp_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'OTP expired.')

    def test_otp_verification_invalid_otp(self):
        data = {
            'email': self.pending_user.email,
            'otp': 'invalid-otp'
        }
        response = self.client.post(self.verify_otp_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Invalid OTP.')

class PasswordSetupTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.verify_otp_url = reverse('verify-otp')
        self.set_password_url = reverse('set-password')

        # Register and verify OTP for the user
        self.client.post(self.register_url, {'username': 'testuser', 'email': 'testuser@example.com'}, format='json')
        self.pending_user = PendingRegistration.objects.first()
        self.pending_user.generate_otp()
        self.client.post(self.verify_otp_url, {'email': self.pending_user.email, 'otp': self.pending_user.otp}, format='json')

    def test_password_setup_success(self):
        reset_token = self.pending_user.reset_token
        data = {
            'email': self.pending_user.email,
            'password': 'newpassword123'
        }
        response = self.client.post(self.set_password_url, data, format='json', **{'HTTP_X_RESET_TOKEN': reset_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.filter(email=self.pending_user.email).exists())
        self.assertFalse(PendingRegistration.objects.filter(email=self.pending_user.email).exists())

    def test_password_setup_invalid_token(self):
        data = {
            'email': self.pending_user.email,
            'password': 'newpassword123'
        }
        response = self.client.post(self.set_password_url, data, format='json', **{'HTTP_X_RESET_TOKEN': 'invalid-token'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Invalid or expired token.')

    def test_password_setup_no_token(self):
        data = {
            'email': self.pending_user.email,
            'password': 'newpassword123'
        }
        response = self.client.post(self.set_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Reset token missing in headers.')
