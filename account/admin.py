# account/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from account.models import User, Customer

# ---------------- USER ADMIN ----------------
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username', 'email', 'image_tag', 'country', 'city', 'home_city', 
        'zip_code', 'phone', 'address', 'created_at', 'updated_at', 
        'is_staff', 'is_active'
    )
    search_fields = ('username', 'email', 'phone', 'country', 'city')
    ordering = ('id',)
    list_filter = ('is_staff', 'is_active')

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

# ---------------- CUSTOMER ADMIN ----------------
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'get_username', 'get_email', 'image_tag', 'phone', 'city', 'country', 'created_at', 'updated_at'
    )
    search_fields = ('user__username', 'user__email', 'phone', 'city', 'country')
    ordering = ('id',)

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

admin.site.register(Customer, CustomerAdmin)
