# models.py
from django.db import models

class Train(models.Model):
    train_name = models.CharField(max_length=100)
    route = models.CharField(max_length=255)
    journey_time = models.DurationField()
    arrival_time = models.TimeField()
    total_seats = models.IntegerField()
    available_seats = models.IntegerField()

    def __str__(self):
        return self.train_name

class TicketClass(models.Model):
    train = models.ForeignKey(Train, related_name='ticket_classes', on_delete=models.CASCADE)
    class_name = models.CharField(max_length=50)  # e.g., Sleeper, AC, General
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_seats = models.IntegerField(default=0)  # Total seats in this class
    available_seats = models.IntegerField(default=0)  # Available seats in this class


    def __str__(self):
        return f"{self.class_name} - {self.train.train_name}"
