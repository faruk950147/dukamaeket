from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from account.models import User, Profile

# ---------------- PROFILE INLINE ----------------
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    readonly_fields = ('image_tag',)
    fieldsets = (
        (None, {'fields': ('image', 'image_tag', 'country', 'city', 'home_city', 'zip_code', 'phone', 'address')}),
    )

# ---------------- USER ADMIN ----------------
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    search_fields = ('username', 'email')
    ordering = ('id',)
    inlines = (ProfileInline,)

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

# ---------------- REGISTER ----------------
admin.site.register(User, UserAdmin)
admin.site.register(Profile)
