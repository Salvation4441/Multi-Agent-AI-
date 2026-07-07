from django.db import models
from django.contrib.auth.models import User

# --------------------------
# Product Model
# --------------------------
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50)
    in_stock = models.BooleanField(default=True)

    def __str__(self):
        return self.name






# --------------------------
# Orders Model
# --------------------------
class Order(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('dispatched', 'Dispatched'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True,related_name='orders')
    product_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    carrier = models.CharField(max_length=100, blank=True, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    delivery = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True,null=True,blank=True)

    def __str__(self):
        return f"Order #{self.id} - {self.product.name} ({self.status})"



# --------------------------
# Refund Request Model
# --------------------------
class RefundRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('delivered', 'Delivered'),
    ]


    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='refund_requests')
    order = models.ForeignKey(Order, on_delete=models.CASCADE,related_name='refund_requests')
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField()



    def __str__(self):
        return f"Refund Request Order #{self.order.id} - {self.user.username} - {self.status}"