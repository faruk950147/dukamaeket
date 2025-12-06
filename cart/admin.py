from django.contrib import admin
from .models import Cart, Wishlist, Coupon

# =========================================================
# 01. COUPON ADMIN
# =========================================================
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'code', 'discount_type', 'discount_value', 'active',
        'min_purchase', 'expiry_date', 'created_at', 'updated_at'
    )
    list_filter = ('active', 'discount_type')
    search_fields = ('code',)
    ordering = ('id',)


# =========================================================
# 02. CART ADMIN
# =========================================================
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'product', 'variant', 'quantity', 'unit_price',
        'subtotal', 'coupon', 'discount_amount', 'total_price', 'paid',
        'created_at', 'updated_at'
    )
    list_filter = ('paid',)
    search_fields = ('user__username', 'product__title')
    readonly_fields = (
        'unit_price', 'subtotal', 'discount_amount', 'total_price',
        'created_at', 'updated_at'
    )
    autocomplete_fields = ('user', 'product', 'variant', 'coupon')
    ordering = ('id',)


# =========================================================
# 03. WISHLIST ADMIN
# =========================================================
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'variant', 'created_at')
    search_fields = ('user__username', 'product__title')
    autocomplete_fields = ('user', 'product', 'variant')
    ordering = ('id',)
