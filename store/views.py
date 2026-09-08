from django.shortcuts import render, get_object_or_404
from category.models import Product, Category
from django.core.paginator import Paginator
from django.db.models import Q


def store(request, category_slug=None):
    if not request.session.session_key:
        request.session.create()
    if category_slug:
        categorie = get_object_or_404(Category, slug=category_slug)
        # print(categorie)
        product = Product.objects.filter(is_available=True, category=categorie).order_by('id')
        paginator = Paginator(product, 3)
        page = request.GET.get('page')
        page_number = paginator.get_page(page)
    else:
        product = Product.objects.filter(is_available=True).order_by('id')
        # print(product)
        paginator = Paginator(product, 9)
        # print(paginator.num_pages)
        page = request.GET.get('page')
        page_number = paginator.get_page(page)
    category = Category.objects.all()
    # print(category)
    context = {'products': page_number, 'categories': category, 'total_item': product}
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    single_product = Product.objects.get(slug=product_slug, category__slug=category_slug)
    return render(request, 'store/product-detail.html', {'context': single_product})


def search(request):
    query = request.GET.get('query', '')
    category_id = request.GET.get('category', '')

    products = Product.objects.filter(
        Q(product_name__icontains=query) | Q(description__icontains=query)
    ).order_by('id')

    if category_id:
        products = products.filter(category_id=category_id)

    paginator = Paginator(products, 9)
    page = request.GET.get('page')
    page_number = paginator.get_page(page)

    context = {
        'query': query,
        'category_id': category_id,
        'products': page_number,
        'total_item': products,
    }
    return render(request, 'store/store.html', context)
