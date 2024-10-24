# accounts/urls.py
from django.urls import path
from .views import LockSeatsView, GiveOrderView, OrderDetailView, ConfirmedOrderView


urlpatterns = [
    path('lock/', LockSeatsView.as_view(), name='lock'),
    path('giveOrder/', GiveOrderView.as_view(), name='give order'),
    path('details/', OrderDetailView.as_view(), name='order details'),
    path('confirmOrder/', ConfirmedOrderView.as_view(), name='confirm order'),
]
