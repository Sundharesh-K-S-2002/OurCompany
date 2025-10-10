from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class reg(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    number = models.CharField(max_length=15)
    role = models.CharField(
        max_length=50,
        choices=[('admin', 'Admin'), ('user', 'User')],
        default='user'
    )


    def __str__(self):
        return self.username

class Products(models.Model):
    productimage = models.ImageField(upload_to='products/')
    productname = models.CharField(max_length=100)
    productcode = models.CharField(max_length=100)
    price = models.IntegerField()
    quantity = models.PositiveBigIntegerField()

    def __str__(self):
        return self.productname
    

class Order(models.Model):
    razorpay_order_id = models.CharField(max_length=100, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='created')
    created_at = models.DateTimeField(auto_now_add=True)
    # Add other fields as needed (e.g., user, cart items, etc.)

    def __str__(self):
        return self.razorpay_order_id