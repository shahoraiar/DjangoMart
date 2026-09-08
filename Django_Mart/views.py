from django.shortcuts import render
from category.models import Category, Product
from django.core.paginator import Paginator


def home(request):
    if not request.session.session_key:
        request.session.create()

    product = Product.objects.filter(is_available=True).order_by('id')
    # print(product)
    paginator = Paginator(product, 12)
    # print(paginator.num_pages)
    page = request.GET.get('page')
    page_number = paginator.get_page(page)
    category = Category.objects.all()
    # print(category)
    context = {'products': page_number, 'categories': category, 'total_item': product}
    return render(request, 'index.html', context)
