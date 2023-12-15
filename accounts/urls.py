from django.urls import path , include
from . import views
urlpatterns = [
    path('register/', views.register , name='register'), #accounts/
    path('profile/', views.profile , name='profile'),
    path('signin/', views.signin , name='signin'),
    path('logout/', views.user_logout , name='logout'),
]