from django.contrib import admin
from store.models import (
    Category,
    Brand,
    Product,
    Color,
    Size,
    Slider,
    Review,
    ImageGallery
)

# ---------------- CATEGORY ----------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'created_date', 'image_tag')
    list_filter = ('status', 'created_date')
    search_fields = ('title', 'keyword', 'description')
    readonly_fields = ('image_tag',)

# ---------------- BRAND ----------------
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'created_date', 'image_tag')
    list_filter = ('status', 'created_date')
    search_fields = ('title', 'keyword', 'description')
    readonly_fields = ('image_tag',)

# ---------------- PRODUCT ----------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'brand', 'sale_price', 'available_stock', 'status', 'image_tag')
    list_filter = ('status', 'category', 'brand', 'created_date')
    search_fields = ('title', 'keyword', 'description')
    readonly_fields = ('image_tag', 'average_review', 'count_review', 'remaining')
    fieldsets = (
        (None, {
            'fields': ('title', 'category', 'brand', 'old_price', 'sale_price', 'discount_percent', 'available_stock', 'keyword', 'description', 'image', 'deadline', 'is_timeline', 'status')
        }),
        ('Statistics', {
            'fields': ('average_review', 'count_review', 'remaining')
        }),
    )

# ---------------- IMAGE GALLERY ----------------
@admin.register(ImageGallery)
class ImageGalleryAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'image_tag', 'created_date')
    readonly_fields = ('image_tag',)
    search_fields = ('product__title',)

# ---------------- COLOR ----------------
@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'code', 'color_tag', 'created_date')
    readonly_fields = ('color_tag',)
    search_fields = ('title', 'code')

# ---------------- SIZE ----------------
@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'code', 'created_date')
    search_fields = ('title', 'code')

# ---------------- SLIDER ----------------
@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'image_tag', 'created_date')
    list_filter = ('status', 'created_date')
    readonly_fields = ('image_tag',)
    search_fields = ('title',)

# ---------------- REVIEW ----------------
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'subject', 'rate', 'status', 'created_date')
    list_filter = ('status', 'rate', 'created_date')
    search_fields = ('product__title', 'user__username', 'subject', 'comment')
