from django.contrib import admin
from cart.models import Coupon, Cart, Wishlist

# =========================================================
# COUPON ADMIN
# =========================================================
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'discount_type', 'discount_value', 'active', 'min_purchase', 'expiry_date', 'created_at', 'updated_at')
    list_filter = ('discount_type', 'active')
    search_fields = ('code',)
    readonly_fields = ('created_at', 'updated_at')


# =========================================================
# CART ADMIN
# =========================================================
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'variant', 'quantity', 'unit_price', 'subtotal', 'discount_amount', 'total_price', 'paid', 'created_at', 'updated_at')
    list_filter = ('paid',)
    search_fields = ('user__username', 'product__title', 'variant__id')
    readonly_fields = ('unit_price', 'subtotal', 'discount_amount', 'total_price', 'created_at', 'updated_at')


# =========================================================
# WISHLIST ADMIN
# =========================================================
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'variant', 'created_at', 'updated_at')
    search_fields = ('user__username', 'product__title', 'variant__id')
    readonly_fields = ('created_at', 'updated_at')
