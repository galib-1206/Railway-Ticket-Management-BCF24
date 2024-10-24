# models.py
from django.db import models

class Payment(models.Model):
    order_id = models.CharField(max_length=255)
    payment_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50)  # Example: "successful", "failed", etc.
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Payment {self.payment_id} for Order {self.order_id}"
