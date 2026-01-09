from django.contrib import admin
from .models import Checkout, CheckoutItem

class CheckoutItemInline(admin.TabularInline):
    model = CheckoutItem
    extra = 0
    readonly_fields = ('product', 'variant', 'quantity', 'total_price')
    # Prevent editing quantity or product directly from admin
    can_delete = False

class CheckoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'delivery_method', 'is_checkout', 'created_at', 'total_items', 'total_price')
    list_filter = ('status', 'delivery_method', 'is_checkout', 'created_at')
    search_fields = ('user__username', 'id')
    readonly_fields = ('total_items', 'total_price')
    inlines = [CheckoutItemInline]

    # Optional: show total_items and total_price in admin detail page
    def total_items(self, obj):
        return obj.total_items()
    total_items.short_description = "Total Items"

    def total_price(self, obj):
        return obj.total_price()
    total_price.short_description = "Total Price"

admin.site.register(Checkout, CheckoutAdmin)



""" class CheckoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'profile', 'product', 'variant', 'quantity', 'check_price', 'total_cost', 'status', 'is_ordered', 'payment_method', 'created_at')
    list_filter = ('status', 'is_ordered', 'payment_method', 'created_at')
    search_fields = ('user__username', 'profile__user__username', 'product__title', 'id')
    readonly_fields = ('total_cost', 'check_price')
    actions = ['mark_selected_as_ordered']

    # Show total_cost in admin
    def total_cost(self, obj):
        return obj.total_cost
    total_cost.short_description = "Total Cost"

    # Custom admin action to mark multiple orders as ordered
    def mark_selected_as_ordered(self, request, queryset):
        for checkout in queryset:
            if not checkout.is_ordered:
                try:
                    checkout.mark_as_ordered()
                except ValueError as e:
                    self.message_user(request, f"Error for order #{checkout.id}: {str(e)}", level='error')
        self.message_user(request, "Selected orders have been processed.")
    mark_selected_as_ordered.short_description = "Mark selected orders as Ordered"

admin.site.register(Checkout, CheckoutAdmin)
 """