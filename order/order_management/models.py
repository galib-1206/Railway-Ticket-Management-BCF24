from django.db import models

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    user_id = models.IntegerField()  # Storing user ID from the auth service
    train_id = models.IntegerField()  # Storing train ID from train service
    ticket_class = models.CharField(max_length=50)
    number_of_seats = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by User #{self.user_id}"
