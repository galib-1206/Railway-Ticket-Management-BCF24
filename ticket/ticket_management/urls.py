# urls.py
from django.urls import path
from .views import TrainListView, TrainDetailView

urlpatterns = [
    path('trains/', TrainListView.as_view(), name='train-list'),
    path('trains/<int:id>/', TrainDetailView.as_view(), name='train-detail'),
]
