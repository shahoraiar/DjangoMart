from django.shortcuts import render,redirect
from .forms import RegisterForm
from django.contrib.auth import login,logout,authenticate
from cart.models import Cart , CartItem
# Create your views here.

def register(request) : 
    form = RegisterForm()
    if request.method == 'POST' : 
        form = RegisterForm(request.POST)
        if form.is_valid() : 
            user = form.save()
            login(request , user)
            return redirect('profile')
    return render(request , 'accounts/register.html' , {'form' : form})

def profile(request) : 
    return render(request , 'accounts/dashboard.html')

def signin(request):
    if request.method == 'POST':
        user_name = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=user_name, password=password)

        if user is not None:
            # Login successful
            if not request.session.session_key:
                request.session.create()
            session_id = request.session.session_key

            try:
                cart = Cart.objects.get(cart_id=session_id)
            except Cart.DoesNotExist:
                cart = None

            is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()

            if is_cart_item_exists:
                cart_item = CartItem.objects.filter(cart=cart)
                for item in cart_item:
                    item.user = user
                    item.save()

            login(request, user)
            return redirect('cart')
        else:
            # Login failed, redirect to 'register'
            return redirect('register')  # Make sure to replace 'register' with your actual URL name

    return render(request, 'accounts/signin.html')

def user_logout(request) : 
    logout(request)
    return redirect('signin')