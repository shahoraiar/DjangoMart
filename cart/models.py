from django.db import models
from category.models import Product
from django.contrib.auth.models import User
# Create your models here.
class Cart(models.Model) : 
    cart_id = models.CharField(max_length=250 , blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) :
        return self.cart_id

class CartItem(models.Model) : 
    product = models.ForeignKey(Product , on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart , on_delete= models.CASCADE , null= True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(User , on_delete=models.CASCADE , null=True)

    def sub_calculte(self) : 
        return self.product.price * self.quantity
    def __str__(self) :
        return f"{self.product.product_name}"
    
