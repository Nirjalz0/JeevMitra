from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets=UserAdmin.fieldsets + (
        ('Jeev Mitra', {'fields': ('role','is_verified','phone')}),
    )
    list_display=('username','email','role','is_verified','is_staff')
    list_filter=('role','is_verified')

# Register your models here.
