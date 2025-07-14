from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
# Register your models here.
class CustomUserAdmin(UserAdmin):
    readonly_fields = ['date_joined']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Role Info', {'fields': ('role',)}),
        ('Manager', {'fields': ('manager',)}),
    )
    list_display = ('username', 'email', 'role', 'date_joined','is_staff','manager')

admin.site.register(CustomUser, CustomUserAdmin)
