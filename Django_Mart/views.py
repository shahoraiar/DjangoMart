from django.shortcuts import render
from category.models import Category , Product
from django.core.paginator import Paginator

def home(request) : 
    if not request.session.session_key:
        request.session.create()
    
    product = Product.objects.filter(is_available = True)
    # print(product)
    paginator = Paginator(product, 12) # 1 page 9 products
    # print(paginator.num_pages)
    page = request.GET.get('page')#frontend theke nibe kon page e jabo ;
    page_number = paginator.get_page(page) #kon page number e aci ;
    category = Category.objects.all() #frontend print all category name 
    # print(category)
    context = {'products' : page_number , 'categories' : category ,'total_item' : product}
    return render(request , 'index.html' , context)

# def base(request) : 
#     category = Category.objects.all()
#     print(category.category_name)
#     return render(request , 'base.html' , {'categories' : category })