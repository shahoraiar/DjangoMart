import string
import random

from sslcommerz_lib import SSLCOMMERZ

from .models import PaymentGateWaySettings


def unique_transaction_id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def sslcommerz_payment_gateway(request, order_id, user_id, grand_total, order=None):
    gateway_auth_details = PaymentGateWaySettings.objects.all().first()
    if not gateway_auth_details:
        raise RuntimeError('Payment gateway settings not configured.')

    settings = {
        'store_id': gateway_auth_details.store_id,
        'store_pass': gateway_auth_details.store_pass,
        'issandbox': True,
    }
    sslcommez = SSLCOMMERZ(settings)

    email = getattr(order, 'email', None) or getattr(request.user, 'email', '') or 'customer@example.com'
    phone = getattr(order, 'phone', None) or '01700000000'
    address = getattr(order, 'address_line1', None) or 'N/A'
    city = getattr(order, 'city', None) or 'Dhaka'

    post_body = {
        'total_amount': grand_total,
        'currency': 'BDT',
        'tran_id': unique_transaction_id_generator(),
        'success_url': 'http://127.0.0.1:8000/order/success/',
        'fail_url': 'http://127.0.0.1:8000/order/place_order/',
        'cancel_url': 'http://127.0.0.1:8000/',
        'emi_option': 0,
        'cus_name': f'{getattr(order, "first_name", "")} {getattr(order, "last_name", "")}'.strip() or request.user.username,
        'cus_email': email,
        'cus_phone': phone,
        'cus_add1': address,
        'cus_city': city,
        'cus_country': getattr(order, 'country', None) or 'Bangladesh',
        'shipping_method': 'NO',
        'multi_card_name': '',
        'num_of_item': 1,
        'product_name': 'DjangoMart Order',
        'product_category': 'General',
        'product_profile': 'general',
        'value_a': str(order_id),
        'value_b': str(user_id),
        'value_c': email,
    }

    response = sslcommez.createSession(post_body)
    # print('sslcommerz response:', response)

    if not response or response.get('status') != 'SUCCESS':
        reason = (response or {}).get('failedreason') or 'Unknown SSLCommerz error'
        raise RuntimeError(reason)

    payment_url = response.get('GatewayPageURL') or response.get('redirectGatewayURL')
    if not payment_url and response.get('sessionkey'):
        payment_url = (
            'https://sandbox.sslcommerz.com/gwprocess/v4/gw.php'
            f'?Q=pay&SESSIONKEY={response["sessionkey"]}'
        )

    if not payment_url:
        raise RuntimeError('Payment redirect URL missing from SSLCommerz response.')

    return payment_url
