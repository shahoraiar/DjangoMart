from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group
from unfold.admin import ModelAdmin

from .models import EmailOTP

admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    pass


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


@admin.register(EmailOTP)
class EmailOTPAdmin(ModelAdmin):
    list_display = ('email', 'otp', 'purpose', 'created_at', 'is_used')
    list_filter = ('purpose', 'is_used')
    search_fields = ('email', 'otp')
