from django.contrib import admin
from .models import (
    Category, Brand, Product, ProductVariant, ImageGallery,
    Color, Size, Slider, Review, AcceptancePayment
)

# =========================================================
# 01. IMAGE PREVIEW MIXIN FOR ADMIN
# =========================================================
class ImagePreviewMixin:
    readonly_fields = ('image_tag',)

# =========================================================
# 02. CATEGORY ADMIN
# =========================================================
class CategoryAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('id', 'title', 'slug', 'parent', 'keyword', 'description',
                    'status', 'is_featured', 'created_date', 'updated_date', 'image_tag')
    list_filter = ('status', 'is_featured')
    search_fields = ('title', 'keyword', 'description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_date', 'updated_date', 'image_tag')
    ordering = ('id',)

admin.site.register(Category, CategoryAdmin)

# =========================================================
# 03. BRAND ADMIN
# =========================================================
class BrandAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('id', 'title', 'slug', 'keyword', 'description',
                    'status', 'is_featured', 'created_date', 'updated_date', 'image_tag')
    list_filter = ('status', 'is_featured')
    search_fields = ('title', 'keyword', 'description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_date', 'updated_date', 'image_tag')
    ordering = ('id',)

admin.site.register(Brand, BrandAdmin)

# =========================================================
# 04. IMAGE GALLERY INLINE
# =========================================================
class ImageGalleryInline(ImagePreviewMixin, admin.TabularInline):
    model = ImageGallery
    extra = 1
    fields = ('id', 'product', 'image', 'created_date', 'updated_date', 'image_tag')
    readonly_fields = ('created_date', 'updated_date', 'image_tag')

# =========================================================
# 05. PRODUCT VARIANT INLINE
# =========================================================
class ProductVariantInline(ImagePreviewMixin, admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('id', 'product', 'color', 'size', 'image', 'variant_price', 'available_stock', 
              'status', 'created_date', 'updated_date', 'image_tag')
    readonly_fields = ('created_date', 'updated_date')

# =========================================================
# 06. PRODUCT ADMIN
# =========================================================
class ProductAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('id', 'title', 'slug', 'category', 'brand', 'old_price', 'sale_price',
                    'available_stock', 'discount_percent', 'keyword', 'description',
                    'deadline', 'is_deadline', 'is_featured', 'sold', 'status',
                    'created_date', 'updated_date', 'sold_percentage', 'average_review', 'count_review', 'remaining_seconds', 'image_tag')
    list_filter = ('status', 'is_featured', 'category', 'brand')
    search_fields = ('title', 'keyword', 'description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_date', 'updated_date', 'sold_percentage', 'average_review', 'count_review', 'remaining_seconds', 'image_tag')
    inlines = [ImageGalleryInline, ProductVariantInline]
    ordering = ('id',)

admin.site.register(Product, ProductAdmin)

# =========================================================
# 07. COLOR ADMIN
# =========================================================
class ColorAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('id', 'title', 'code', 'created_date', 'updated_date', 'color_tag')
    search_fields = ('title', 'code')
    readonly_fields = ('created_date', 'updated_date', 'color_tag')

admin.site.register(Color, ColorAdmin)

# =========================================================
# 08. SIZE ADMIN
# =========================================================
class SizeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'code', 'created_date', 'updated_date')
    search_fields = ('title', 'code')
    readonly_fields = ('created_date', 'updated_date')

admin.site.register(Size, SizeAdmin)

# =========================================================
# 09. SLIDER ADMIN
# =========================================================
class SliderAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('id', 'title', 'slider_type', 'product', 'sub_title', 'paragraph', 'status', 'created_date', 'updated_date', 'image_tag')
    list_filter = ('slider_type', 'status')
    search_fields = ('title', 'sub_title', 'paragraph')
    readonly_fields = ('created_date', 'updated_date', 'image_tag')
    prepopulated_fields = {'title': ('title',)}

admin.site.register(Slider, SliderAdmin)

# =========================================================
# 10. REVIEW ADMIN
# =========================================================
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'subject', 'comment', 'rating', 'status', 'created_date', 'updated_date')
    list_filter = ('status', 'rating')
    search_fields = ('product__title', 'user__username', 'subject', 'comment')
    readonly_fields = ('created_date', 'updated_date')

admin.site.register(Review, ReviewAdmin)

# =========================================================
# 11. ACCEPTANCE PAYMENT ADMIN
# =========================================================
class AcceptancePaymentAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('id', 'title', 'sub_title', 'status', 'is_featured', 'help_time', 'created_date', 'updated_date', 'image_tag')
    list_filter = ('status', 'is_featured')
    search_fields = ('title', 'sub_title')
    readonly_fields = ('created_date', 'updated_date', 'image_tag')

admin.site.register(AcceptancePayment, AcceptancePaymentAdmin)
