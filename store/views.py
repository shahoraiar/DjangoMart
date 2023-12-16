from django.shortcuts import render , get_object_or_404
from category.models import Product , Category
from django.core.paginator import Paginator
from django.db.models import Q
# Create your views here.

def store(request , category_slug=None) : 
    if not request.session.session_key:
        request.session.create()
    if category_slug : 
        categorie = get_object_or_404(Category , slug = category_slug)
        # print(categorie)
        product = Product.objects.filter(is_available = True , category=categorie)
        paginator = Paginator(product,3) #1 page e 3 ta product
        page = request.GET.get('page') #came from frontened
        page_number = paginator.get_page(page) #kon page e ace ; page = 2
    else :
        product = Product.objects.filter(is_available = True)
        # print(product)
        paginator = Paginator(product, 9) # 1 page 9 products
        # print(paginator.num_pages)
        page = request.GET.get('page')#frontend theke nibe kon page e jabo ;
        page_number = paginator.get_page(page) #kon page number e aci ;
    category = Category.objects.all() #frontend print all category name 
    # print(category)
    context = {'products' : page_number , 'categories' : category ,'total_item' : product}
    return render(request , 'store/store.html' , context)

def product_detail(request , category_slug , product_slug) : 
    single_product = Product.objects.get(slug = product_slug , category__slug = category_slug)
    
    return render(request , 'store/product-detail.html' , {'context' : single_product})

# def search(request):
#     query = request.GET.get('query', '')
#     category_id = request.GET.get('category', '')

#     # Filter products based on the search query and category
#     products = Product.objects.filter(Q(product_name__icontains=query) | Q(description__icontains=query))

#     if category_id:
#         products = products.filter(category_id=category_id)

#     context = {'query': query, 'category_id': category_id, 'products': products ,'total_item' : products}
#     return render(request, 'store/store.html', context)

def search(request):
    query = request.GET.get('query', '')
    category_id = request.GET.get('category', '')

    # Filter products based on the search query and category
    products = Product.objects.filter(Q(product_name__icontains=query) | Q(description__icontains=query))

    if category_id:
        products = products.filter(category_id=category_id)

    # Paginate the search results
    paginator = Paginator(products, 9)  # Change the number per page if needed
    page = request.GET.get('page')
    page_number = paginator.get_page(page)

    context = {'query': query, 'category_id': category_id, 'products': page_number, 'total_item': products}
    return render(request, 'store/store.html', context)