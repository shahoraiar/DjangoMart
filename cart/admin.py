from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Cart, CartItem


@admin.register(Cart)
class CartAdmin(ModelAdmin):
    list_display = ('cart_id', 'date_added')
    search_fields = ('cart_id',)


@admin.register(CartItem)
class CartItemAdmin(ModelAdmin):
    list_display = ('product', 'cart', 'user', 'quantity', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('product__product_name',)
