# ScheduleBuddy/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'user_type', 'church')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('user_type', 'church')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
