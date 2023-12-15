from django.urls import path
from . import views
urlpatterns = [
    path('', views.cart , name='cart'), #cart/
    path('<int:product_id>/', views.add_to_cart , name='add_to_cart'), #cart/
    path('decrease/<int:product_id>/', views.decrease_cart , name='decrease_cart'), #cart/
    path('delete/<int:product_id>/', views.remove , name='remove'), #cart/
    
]