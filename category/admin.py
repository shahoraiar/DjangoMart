from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = ('category_name', 'slug')
    search_fields = ('category_name',)


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    prepopulated_fields = {'slug': ('product_name',)}
    list_display = (
        'product_name', 'category', 'price', 'stock',
        'is_available', 'created_date', 'modified_date',
    )
    list_filter = ('is_available', 'category')
    search_fields = ('product_name',)
