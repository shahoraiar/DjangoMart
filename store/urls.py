from django.urls import path
from .import views

urlpatterns = [
    path('',views.store , name='store'), #store
    path('category/<slug:category_slug>/', views.store , name='product_by_category'), #store
    path('<slug:category_slug>/<slug:product_slug>/',views.product_detail , name='product-details') ,
    path('search/', views.search, name='search'),
]
