import random
from datetime import timedelta

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from django.utils.html import escape

from .models import EmailOTP


def generate_otp_code():
    return f'{random.randint(100000, 999999)}'


def _otp_email_html(code, purpose, minutes=5):
    if purpose == EmailOTP.PURPOSE_REGISTER:
        headline = 'Verify your registration'
        intro = 'Use this one-time password to complete your DjangoMart signup.'
    else:
        headline = 'Reset your password'
        intro = 'Use this one-time password to reset your DjangoMart account password.'

    safe_code = escape(code)
    return f'''<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body style="margin:0;padding:0;background:#f4f6f8;font-family:Segoe UI,Arial,sans-serif;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f4f6f8;padding:32px 12px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:480px;background:#ffffff;border-radius:14px;overflow:hidden;border:1px solid #e8ecf0;">
          <tr>
            <td style="background:#3167eb;padding:22px 28px;text-align:center;">
              <div style="color:#ffffff;font-size:22px;font-weight:700;letter-spacing:0.3px;">DjangoMart</div>
            </td>
          </tr>
          <tr>
            <td style="padding:28px 28px 8px;text-align:center;">
              <div style="color:#1f2937;font-size:18px;font-weight:700;margin-bottom:8px;">{escape(headline)}</div>
              <div style="color:#6b7280;font-size:14px;line-height:1.5;">{escape(intro)}</div>
            </td>
          </tr>
          <tr>
            <td style="padding:18px 28px 8px;text-align:center;">
              <div style="display:inline-block;background:#f0f4ff;border:1px dashed #3167eb;border-radius:12px;padding:16px 28px;">
                <div style="color:#6b7280;font-size:12px;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">Your OTP</div>
                <div style="color:#3167eb;font-size:32px;font-weight:800;letter-spacing:8px;font-family:Consolas,Monaco,monospace;">{safe_code}</div>
              </div>
            </td>
          </tr>
          <tr>
            <td style="padding:16px 28px 28px;text-align:center;">
              <div style="color:#b45309;background:#fffbeb;border-radius:8px;padding:10px 14px;font-size:13px;display:inline-block;">
                Expires in <strong>{minutes} minutes</strong>
              </div>
              <div style="color:#9ca3af;font-size:12px;line-height:1.5;margin-top:16px;">
                If you did not request this, you can safely ignore this email.
              </div>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>'''


def create_and_send_otp(email, purpose):
    """Invalidate old OTPs, create a new one, and email it. Expires in 5 minutes."""
    EmailOTP.objects.filter(
        email__iexact=email,
        purpose=purpose,
        is_used=False,
    ).update(is_used=True)

    minutes = getattr(settings, 'OTP_EXPIRY_MINUTES', 5)
    code = generate_otp_code()
    otp_obj = EmailOTP.objects.create(email=email.lower(), otp=code, purpose=purpose)

    if purpose == EmailOTP.PURPOSE_REGISTER:
        subject = 'DjangoMart — Your registration OTP'
        text = (
            f'DjangoMart registration OTP\n\n'
            f'Your OTP is: {code}\n'
            f'It expires in {minutes} minutes.\n\n'
            f'If you did not request this, ignore this email.'
        )
    else:
        subject = 'DjangoMart — Your password reset OTP'
        text = (
            f'DjangoMart password reset OTP\n\n'
            f'Your OTP is: {code}\n'
            f'It expires in {minutes} minutes.\n\n'
            f'If you did not request this, ignore this email.'
        )

    mail = EmailMultiAlternatives(
        subject=subject,
        body=text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
    )
    mail.attach_alternative(_otp_email_html(code, purpose, minutes), 'text/html')
    mail.send(fail_silently=False)
    return otp_obj


def get_latest_otp(email, purpose):
    return (
        EmailOTP.objects.filter(email__iexact=email, purpose=purpose)
        .order_by('-created_at')
        .first()
    )


def seconds_until_otp_expiry(otp_obj, minutes=5):
    if not otp_obj:
        return 0
    expires_at = otp_obj.created_at + timedelta(minutes=minutes)
    remaining = (expires_at - timezone.now()).total_seconds()
    return max(0, int(remaining))
