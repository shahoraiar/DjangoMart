from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Payment, Order, OrderProduct, PaymentGateWaySettings


@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = ('payment_id', 'user', 'payment_method', 'amount_paid', 'status', 'created_at')
    list_filter = ('status', 'payment_method')
    search_fields = ('payment_id', 'user__username')


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = (
        'order_no', 'user', 'full_name_display', 'order_total',
        'status', 'is_ordered', 'created_at',
    )
    list_filter = ('status', 'is_ordered')
    search_fields = ('order_no', 'email', 'phone', 'user__username')

    @admin.display(description='Name')
    def full_name_display(self, obj):
        return obj.full_name()


@admin.register(OrderProduct)
class OrderProductAdmin(ModelAdmin):
    list_display = ('order', 'product', 'user', 'quantity', 'ordered', 'created')
    list_filter = ('ordered',)
    search_fields = ('order__order_no', 'product__product_name')


@admin.register(PaymentGateWaySettings)
class PaymentGateWaySettingsAdmin(ModelAdmin):
    list_display = ('store_id',)
