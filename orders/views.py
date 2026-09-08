from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from cart.models import CartItem
from .models import Payment, Order, OrderProduct
from .forms import OrderForm
from .ssl import sslcommerz_payment_gateway


def _parse_amount(data):
    raw = data.get('store_amount')
    if raw in (None, ''):
        raw = data.get('amount')
    if raw in (None, ''):
        raw = data.get('currency_amount')
    if hasattr(raw, '__iter__') and not isinstance(raw, (str, bytes)):
        raw = next(iter(raw), 0)
    try:
        return float(str(raw).strip())
    except (TypeError, ValueError):
        return 0.0


@csrf_exempt
def success_view(request):
    data = request.POST
    # print('payment success data -------', data)

    if not data:
        messages.error(request, 'Empty payment response.')
        return redirect('profile')

    try:
        user_id = int(data.get('value_b'))
        order_ref = data.get('value_a')
        user = User.objects.get(pk=user_id)
        order = Order.objects.get(user=user, is_ordered=False, order_no=str(order_ref))
    except (TypeError, ValueError, User.DoesNotExist, Order.DoesNotExist):
        # print('success_view lookup error', exc)
        messages.error(request, 'Could not match payment to an order.')
        return redirect('profile')

    gateway_amount = _parse_amount(data)
    amount_paid = order.order_total
    if gateway_amount >= order.order_total * 0.5:
        amount_paid = gateway_amount

    payment = Payment.objects.create(
        user=user,
        payment_id=data.get('tran_id') or data.get('bank_tran_id') or f'PAY-{order.id}',
        payment_method=data.get('card_issuer') or data.get('card_type') or data.get('card_brand') or 'SSLCommerz',
        amount_paid=amount_paid,
        status=data.get('status') or 'VALID',
    )

    order.payment = payment
    order.is_ordered = True
    order.status = 'accepted'
    order.save(update_fields=['payment', 'is_ordered', 'status'])

    cart_items = CartItem.objects.filter(user=user)
    for item in cart_items:
        product = item.product
        OrderProduct.objects.create(
            order=order,
            payment=payment,
            user=user,
            product=product,
            quantity=item.quantity,
            ordered=True,
        )
        product.stock = max(product.stock - item.quantity, 0)
        product.save(update_fields=['stock'])

    CartItem.objects.filter(user=user).delete()

    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    messages.success(request, f'Payment successful. Order #{order.order_no} placed.')
    return redirect('profile')


def order_complete(request):
    return render(request, 'orders/order_complete.html')


@login_required(login_url='signin')
def place_order(request):
    # print(request.POST)
    tax = 0
    total = 0
    grand_total = 0
    form = OrderForm()
    payment_error = None

    cart_item = CartItem.objects.filter(user=request.user)
    if cart_item.count() < 1:
        return redirect('store')

    for item in cart_item:
        total += item.product.price * item.quantity
    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user
            form.instance.order_total = grand_total
            form.instance.tax = tax
            form.instance.ip = request.META.get('REMOTE_ADDR')
            form.instance.order_no = 'pending'
            saved_instance = form.save()
            saved_instance.order_no = str(saved_instance.id)
            saved_instance.save(update_fields=['order_no'])
            try:
                payment_url = sslcommerz_payment_gateway(
                    request,
                    saved_instance.id,
                    str(request.user.id),
                    grand_total,
                    order=saved_instance,
                )
                return redirect(payment_url)
            except Exception as exc:
                # print('payment gateway error', exc)
                payment_error = f'Payment gateway error: {exc}'

    return render(request, 'orders/place-order.html', {
        'cart_item': cart_item,
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
        'form': form,
        'payment_error': payment_error,
    })
