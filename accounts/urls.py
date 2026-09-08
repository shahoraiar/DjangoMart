from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('profile/', views.profile, name='profile'),
    path('transactions/', views.transactions, name='transactions'),
    path('settings/', views.account_settings, name='account_settings'),
    path('received-orders/', views.received_orders, name='received_orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('signin/', views.signin, name='signin'),
    path('logout/', views.user_logout, name='logout'),
]
