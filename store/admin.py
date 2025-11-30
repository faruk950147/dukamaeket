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
    list_editable = ('status', 'is_featured')

admin.site.register(Category, CategoryAdmin)

# =========================================================
# 03. BRAND ADMIN
# =========================================================
class BrandAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('id', 'title', 'slug', 'keyword', 'description', 'status', 'is_featured', 'created_date', 'updated_date', 'image_tag')
    list_filter = ('status', 'is_featured')
    search_fields = ('title', 'keyword', 'description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_date', 'updated_date', 'image_tag')
    ordering = ('id',)
    list_editable = ('status', 'is_featured')

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
              'status', 'created_date', 'updated_date')
    readonly_fields = ('created_date', 'updated_date')

# =========================================================
# 06. PRODUCT ADMIN
# =========================================================
class ProductAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('id', 'title', 'slug', 'category', 'brand', 'old_price', 'sale_price',
                    'available_stock', 'discount_percent', 'prev_des', 'add_des', 'short_des', 'long_des', 'keyword', 'description',
                    'tag', 'deadline', 'is_deadline', 'is_featured', 'sold', 'status',
                    'created_date', 'updated_date', 'sold_percentage', 'average_review', 'count_review', 'remaining_seconds')
    list_filter = ('status', 'is_featured', 'category', 'brand')
    search_fields = ('title', 'keyword', 'description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_date', 'updated_date', 'sold_percentage', 'average_review', 'count_review', 'remaining_seconds')
    inlines = [ImageGalleryInline, ProductVariantInline]
    ordering = ('id',)
    list_editable = ('status', 'is_deadline', 'is_featured')

admin.site.register(Product, ProductAdmin)

# =========================================================
# 07. IMAGES GALLERIES ADMIN
# =========================================================
class ImagesGalleriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'image', 'status', 'created_date', 'updated_date')
    readonly_fields = ('created_date', 'updated_date')
    list_filter = ('id', 'product', 'image', 'created_date', 'updated_date')
    search_fields = ('id', 'product')
    ordering = ('id',)
    list_editable = ('status',)
admin.site.register(ImageGallery, ImagesGalleriesAdmin)

# =========================================================
# 08. COLOR ADMIN
# =========================================================
class ColorAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('id', 'title', 'code', 'status', 'created_date', 'updated_date', 'color_tag')
    search_fields = ('title', 'code')
    readonly_fields = ('created_date', 'updated_date', 'color_tag')
    list_editable = ('title', 'code', 'status')

admin.site.register(Color, ColorAdmin)

# =========================================================
# 09. SIZE ADMIN
# =========================================================
class SizeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'code', 'status', 'created_date', 'updated_date')
    search_fields = ('title', 'code')
    readonly_fields = ('created_date', 'updated_date')
    list_editable = ('title', 'code', 'status')

admin.site.register(Size, SizeAdmin)

# =========================================================
# 10. PRODUCT VARIANT ADMIN
# =========================================================
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'color', 'size', 'image', 'variant_price', 'available_stock', 'status', 'created_date', 'updated_date')
    list_filter = ('product', 'color', 'size', 'status')
    search_fields = ('product__title', 'color__title', 'size__title')
    readonly_fields = ('created_date', 'updated_date', 'image')
    list_editable = ('status', 'product', 'color', 'size', 'variant_price', 'available_stock')

admin.site.register(ProductVariant, ProductVariantAdmin)

# =========================================================
# 11. SLIDER ADMIN
# =========================================================
class SliderAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('id', 'title', 'slider_type', 'product', 'sub_title', 'paragraph', 'status', 'created_date', 'updated_date', 'image_tag')
    list_filter = ('slider_type', 'status')
    search_fields = ('title', 'sub_title', 'paragraph')
    readonly_fields = ('created_date', 'updated_date', 'image_tag')
    prepopulated_fields = {'title': ('title',)}
    list_editable = ('status', 'slider_type', 'product', 'sub_title', 'paragraph')

admin.site.register(Slider, SliderAdmin)

# =========================================================
# 12. REVIEW ADMIN
# =========================================================
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'subject', 'comment', 'rating', 'status', 'created_date', 'updated_date')
    list_filter = ('status', 'rating')
    search_fields = ('product__title', 'user__username', 'subject', 'comment')
    readonly_fields = ('created_date', 'updated_date')
    list_editable = ('status', 'product', 'user', 'subject', 'comment', 'rating')
admin.site.register(Review, ReviewAdmin)

# =========================================================
# 13. ACCEPTANCE PAYMENT ADMIN
# =========================================================
class AcceptancePaymentAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('id', 'title', 'sub_title', 'status', 'is_featured', 'help_time', 'created_date', 'updated_date', 'image_tag')
    list_filter = ('status', 'is_featured')
    search_fields = ('title', 'sub_title')
    readonly_fields = ('created_date', 'updated_date', 'image_tag')
    list_editable = ('status', 'title', 'sub_title', 'is_featured', 'help_time')

admin.site.register(AcceptancePayment, AcceptancePaymentAdmin)
