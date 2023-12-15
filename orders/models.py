from django.db import models
from django.contrib.auth.models import User
from category.models import Product

# Create your models here.
class Payment(models.Model) : 
    user = models.ForeignKey(User , on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.IntegerField()
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

class Order(models.Model) :
    STATUS = (
        ('new' , 'NEW'),
        ('accepted' , 'ACCEPTED'),
        ('completed' , 'COMPLETED'),
        ('cancelled' , 'CANCELLED')
    ) 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # payment = models.ForeignKey(Payment , on_delete=models.CASCADE , null=True)
    order_no = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.EmailField(max_length=50)
    address_line1 = models.CharField(max_length=100)
    address_line2 = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    order_note = models.CharField(max_length=100)
    order_total = models.FloatField()
    tax = models.FloatField()
    status = models.CharField(max_length=30 , choices=STATUS, default= 'New')
    ip = models.CharField(max_length=100,blank=True , null=True)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) :
        return self.user.username
    
class OrderProduct(models.Model) : 
    order = models.ForeignKey(Order , on_delete=models.CASCADE)
    Payment = models.ForeignKey(Payment , on_delete=models.CASCADE , null=True)
    user = models.ForeignKey(User , on_delete=models.CASCADE)
    product = models.ForeignKey(Product , on_delete=models.CASCADE)
    quantity = models.IntegerField()
    ordered = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

class PaymentGateWaySettings(models.Model):
    store_id = models.CharField(max_length=500, blank=True, null=True)
    store_pass = models.CharField(max_length=500, blank=True, null = True)
