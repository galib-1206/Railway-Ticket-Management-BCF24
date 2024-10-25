# urls.py
from django.urls import path
from .views import TrainListView, TrainDetailView, AvailableSeatsView, LockSeatsView, UnlockSeatsView

urlpatterns = [
    path('trains/', TrainListView.as_view(), name='train-list'),
    path('trains/<int:id>/', TrainDetailView.as_view(), name='train-detail'),
    path('trains/<int:train_id>/ticket-class/<int:ticket_class_id>/', AvailableSeatsView.as_view(), name='available-seats'),
    path('trains/<int:train_id>/ticket-class/<int:ticket_class_id>/lock/', LockSeatsView.as_view(), name='lock-seats'),
    path('unlock-seats/',UnlockSeatsView.as_view(),name='unlock seats')

    ]
