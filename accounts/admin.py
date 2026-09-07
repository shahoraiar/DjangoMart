from django.contrib import admin
from .models import EmailOTP


@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ('email', 'otp', 'purpose', 'created_at', 'is_used')
    list_filter = ('purpose', 'is_used')
    search_fields = ('email', 'otp')
