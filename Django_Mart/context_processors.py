from cart.models import Cart, CartItem
from category.models import Product , Category

def cart_items(request):
    session_id = request.session.session_key
    cart_item = None

    if request.user.is_authenticated:
        cart_item = CartItem.objects.filter(user=request.user)
    else:
        cart_id = Cart.objects.filter(cart_id=session_id).exists()
        if cart_id:
            modelid = Cart.objects.get(cart_id=session_id)
            cart_item = CartItem.objects.filter(cart=modelid)

    return {'cart_item': cart_item}

def category_name(request) : 
    categories = Category.objects.all()
    return {'categories': categories}
