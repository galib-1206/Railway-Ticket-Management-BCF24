# accounts/urls.py
from django.urls import path
from .views import ProcessPaymentView


urlpatterns = [
    path('pay/', ProcessPaymentView.as_view(), name='make payment')
]
