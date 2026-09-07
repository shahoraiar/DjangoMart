from django.db import models
from django.utils import timezone
from datetime import timedelta


class EmailOTP(models.Model):
    PURPOSE_REGISTER = 'register'
    PURPOSE_RESET = 'reset'
    PURPOSE_CHOICES = [
        (PURPOSE_REGISTER, 'Registration'),
        (PURPOSE_RESET, 'Password Reset'),
    ]

    email = models.EmailField()
    otp = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.email} ({self.purpose}) - {self.otp}'

    def is_expired(self, minutes=5):
        return timezone.now() > self.created_at + timedelta(minutes=minutes)

    def is_valid(self, code, minutes=5):
        return (
            not self.is_used
            and not self.is_expired(minutes)
            and self.otp == code
        )
