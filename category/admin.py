from django.contrib import admin
from . models import Category , Product
# Register your models here.

# admin.site.register(Category)

class CategoryAdmin(admin.ModelAdmin) : 
    prepopulated_fields = {'slug' : ('category_name' ,)}
    list_display = ('category_name' , 'slug')
    
class ProductAdmin(admin.ModelAdmin) : 
    prepopulated_fields = {'slug' : ('product_name' ,)}
    list_display = ('product_name','category' , 'price' , 'stock' , 'is_available'
                    , 'created_date' , 'modified_date')
    
    
admin.site.register(Category , CategoryAdmin)
admin.site.register(Product , ProductAdmin)
