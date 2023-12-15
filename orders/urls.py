from django.urls import path
from . import views

urlpatterns = [
    path('place_order/',views.place_order , name='place_order'), #order
    path('success/',views.success_view , name='success_view'), #order
    path('order_complete/' , views.order_complete , name='order_complete'),
]
