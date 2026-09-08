from django.conf import settings
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect

from .forms import RegisterForm, OTPForm, ForgotPasswordForm, ResetPasswordForm
from .models import EmailOTP
from .utils import (
    create_and_send_otp,
    get_latest_otp,
    seconds_until_otp_expiry,
    merge_session_cart,
    reattach_guest_cart,
)


OTP_MINUTES = getattr(settings, 'OTP_EXPIRY_MINUTES', 5)


def register(request):
    form = RegisterForm()
    error = None

    if request.method == 'POST':
        # Allow restarting unfinished (inactive) signups
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        if username or email:
            User.objects.filter(is_active=False).filter(
                Q(username=username) | Q(email__iexact=email)
            ).delete()

        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].lower()

            user = form.save(commit=False)
            user.email = email
            user.is_active = False
            user.save()

            try:
                create_and_send_otp(email, EmailOTP.PURPOSE_REGISTER)
            except Exception:
                user.delete()
                error = 'Could not send OTP email. Please try again later.'
                return render(request, 'accounts/register.html', {'form': form, 'send_error': error})

            request.session['otp_email'] = email
            request.session['otp_purpose'] = EmailOTP.PURPOSE_REGISTER
            request.session['pending_user_id'] = user.id
            return redirect('verify_otp')

    return render(request, 'accounts/register.html', {'form': form, 'send_error': error})


def verify_otp(request):
    email = request.session.get('otp_email')
    purpose = request.session.get('otp_purpose')
    error = None
    success = None

    if not email or purpose not in (EmailOTP.PURPOSE_REGISTER, EmailOTP.PURPOSE_RESET):
        return redirect('register' if not purpose else 'forgot_password')

    form = OTPForm()
    otp_obj = get_latest_otp(email, purpose)
    remaining = seconds_until_otp_expiry(otp_obj, OTP_MINUTES)

    if request.method == 'POST':
        action = request.POST.get('action', 'verify')

        if action == 'resend':
            try:
                create_and_send_otp(email, purpose)
                success = 'A new OTP has been sent to your email.'
                otp_obj = get_latest_otp(email, purpose)
                remaining = seconds_until_otp_expiry(otp_obj, OTP_MINUTES)
            except Exception:
                error = 'Could not resend OTP. Please try again.'
        else:
            form = OTPForm(request.POST)
            if form.is_valid():
                code = form.cleaned_data['otp'].strip()
                otp_obj = get_latest_otp(email, purpose)

                if not otp_obj:
                    error = 'No OTP found. Please request a new one.'
                elif otp_obj.is_used:
                    error = 'This OTP was already used. Please request a new one.'
                elif otp_obj.is_expired(OTP_MINUTES):
                    error = 'OTP expired (valid for 5 minutes). Please resend OTP.'
                elif otp_obj.otp != code:
                    error = 'Invalid OTP. Please try again.'
                else:
                    otp_obj.is_used = True
                    otp_obj.save(update_fields=['is_used'])

                    if purpose == EmailOTP.PURPOSE_REGISTER:
                        user_id = request.session.get('pending_user_id')
                        try:
                            user = User.objects.get(id=user_id, email__iexact=email)
                        except User.DoesNotExist:
                            error = 'Registration session expired. Please sign up again.'
                            return render(request, 'accounts/verify_otp.html', {
                                'form': form,
                                'email': email,
                                'purpose': purpose,
                                'error': error,
                                'remaining': remaining,
                            })

                        user.is_active = True
                        user.save(update_fields=['is_active'])
                        # Registration only: guest cart → new auth user
                        merge_session_cart(request, user)
                        login(request, user)
                        for key in ('otp_email', 'otp_purpose', 'pending_user_id'):
                            request.session.pop(key, None)
                        return redirect('cart')

                    # Password reset — mark verified then go to set password
                    request.session['otp_verified'] = True
                    return redirect('reset_password')

            remaining = seconds_until_otp_expiry(get_latest_otp(email, purpose), OTP_MINUTES)

    title = 'Verify registration OTP' if purpose == EmailOTP.PURPOSE_REGISTER else 'Verify password reset OTP'
    return render(request, 'accounts/verify_otp.html', {
        'form': form,
        'email': email,
        'purpose': purpose,
        'title': title,
        'error': error,
        'success': success,
        'remaining': remaining,
    })


def forgot_password(request):
    form = ForgotPasswordForm()
    error = None
    info = None

    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].strip().lower()
            try:
                user = User.objects.get(email__iexact=email, is_active=True)
            except User.DoesNotExist:
                error = 'No active account found with this email.'
            else:
                try:
                    create_and_send_otp(email, EmailOTP.PURPOSE_RESET)
                except Exception:
                    error = 'Could not send OTP email. Please try again later.'
                else:
                    request.session['otp_email'] = email
                    request.session['otp_purpose'] = EmailOTP.PURPOSE_RESET
                    request.session['reset_user_id'] = user.id
                    request.session.pop('otp_verified', None)
                    return redirect('verify_otp')

    return render(request, 'accounts/forgot_password.html', {
        'form': form,
        'error': error,
        'info': info,
    })


def reset_password(request):
    email = request.session.get('otp_email')
    purpose = request.session.get('otp_purpose')
    verified = request.session.get('otp_verified')
    user_id = request.session.get('reset_user_id')

    if (
        purpose != EmailOTP.PURPOSE_RESET
        or not verified
        or not email
        or not user_id
    ):
        return redirect('forgot_password')

    try:
        user = User.objects.get(id=user_id, email__iexact=email, is_active=True)
    except User.DoesNotExist:
        return redirect('forgot_password')

    form = ResetPasswordForm(user)
    error = None

    if request.method == 'POST':
        form = ResetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            for key in ('otp_email', 'otp_purpose', 'otp_verified', 'reset_user_id'):
                request.session.pop(key, None)
            return render(request, 'accounts/signin.html', {
                'error': None,
                'username': user.username,
                'success': 'Password updated successfully. Please sign in.',
            })

    return render(request, 'accounts/reset_password.html', {
        'form': form,
        'email': email,
        'error': error,
    })


def profile(request):
    return render(request, 'accounts/dashboard.html')


def signin(request):
    error = None
    success = None
    username = ''

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(username=username, password=password)

        if user is not None:
            # login() changes session key — keep guest cart linked for after logout
            old_session_key = request.session.session_key
            login(request, user)
            reattach_guest_cart(old_session_key, request.session.session_key)
            return redirect('cart')

        # Inactive account (OTP not verified yet)
        inactive = User.objects.filter(username=username, is_active=False).first()
        if inactive and inactive.check_password(password):
            error = 'Account not verified. Complete OTP verification or register again.'
            request.session['otp_email'] = inactive.email
            request.session['otp_purpose'] = EmailOTP.PURPOSE_REGISTER
            request.session['pending_user_id'] = inactive.id
        else:
            error = 'Invalid username or password. Please try again.'

    return render(request, 'accounts/signin.html', {
        'error': error,
        'success': success,
        'username': username,
    })


def user_logout(request):
    # logout() flushes session — reattach guest cart to the new session key
    old_session_key = request.session.session_key
    logout(request)
    if not request.session.session_key:
        request.session.create()
    reattach_guest_cart(old_session_key, request.session.session_key)
    return redirect('signin')
