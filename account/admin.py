# account/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from account.models import User, Customer

# Inline Customer inside User admin
class CustomerInline(admin.StackedInline):
    model = Customer
    can_delete = False
    verbose_name_plural = 'Customer Profile'
    readonly_fields = ('image_tag',)  # Image preview

class UserAdmin(BaseUserAdmin):
    inlines = (CustomerInline,)
    list_display = ('username', 'email', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('id',)

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'image')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )

admin.site.register(User, UserAdmin)
