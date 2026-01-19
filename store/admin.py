from django.contrib import admin
from store.models import (
    Category, Brand, Color, Size,
    Product, ProductVariant, ImageGallery,
    Slider, Review, AcceptancePayment
)

# =========================================================
# IMAGE PREVIEW MIXIN
# =========================================================
class ImagePreviewMixin:
    readonly_fields = ('image_tag',)


# =========================================================
# CATEGORY ADMIN
# =========================================================
@admin.register(Category)
class CategoryAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('id', 'parent', 'title', 'slug', 'keyword', 'description', 'status', 'is_featured', 'image_tag', 'created_at', 'updated_at')
    list_filter = ('status', 'is_featured')
    search_fields = ('title', 'keyword', 'description')
    list_editable = ('parent', 'status', 'is_featured')
    readonly_fields = ('image_tag',)
# =========================================================
# BRAND ADMIN
# =========================================================
@admin.register(Brand)
class BrandAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('id',  'title', 'slug', 'keyword', 'description', 'status', 'is_featured', 'image_tag', 'created_at', 'updated_at')
    list_filter = ('status', 'is_featured')
    search_fields = ('title', 'keyword', 'description')
    list_editable = ('status', 'is_featured')
    readonly_fields = ('image_tag',) 


# =========================================================
# COLOR ADMIN
# =========================================================
@admin.register(Color)
class ColorAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('id', 'title', 'code', 'color_tag', 'status', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('title', 'code')
    list_editable = ('status',)
    readonly_fields = ('color_tag',)


# =========================================================
# SIZE ADMIN
# =========================================================
@admin.register(Size)
class SizeAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('id', 'title', 'code', 'status', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('title', 'code')


# =========================================================
# PRODUCT VARIANT INLINE
# =========================================================
class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    readonly_fields = ('image_tag',)
    fields = ('color', 'size', 'variant_price', 'available_stock', 'status', 'image_id', 'image_tag')


# =========================================================
# IMAGE GALLERY INLINE
# =========================================================
class ImageGalleryInline(admin.TabularInline):
    model = ImageGallery
    extra = 1
    readonly_fields = ('image_tag',)
    fields = ('image', 'status', 'image_tag')


# =========================================================
# REVIEW INLINE
# =========================================================
class ReviewInline(admin.TabularInline):
    model = Review
    extra = 1
    readonly_fields = ('user', 'created_at', 'updated_at')


# =========================================================
# PRODUCT ADMIN
# =========================================================
@admin.register(Product)
class ProductAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('id','category', 'brand', 'variant', 'title', 'sale_price', 'available_stock',
                    'sold', 'sold_percentage', 'average_review', 'status', 'is_featured', 'is_deadline', 'image_tag')
    list_filter = ('status', 'is_featured', 'category', 'brand')
    search_fields = ('title', 'keyword', 'description', 'tag')
    readonly_fields = ('slug', 'image_tag', 'sold_percentage', 'average_review', 'total_available_stock')
    inlines = [ProductVariantInline, ImageGalleryInline, ReviewInline]
    list_editable = ('status', 'is_featured', 'is_deadline', 'available_stock')



# =========================================================
# ProductVariant ADMIN
# =========================================================
@admin.register(ProductVariant)
class ProductVariantAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('id', 'title', 'product', 'color', 'size', 'image_id', 'sku', 'final_price', 'available_stock', 'status', 'image_tag')
    list_filter = ('status', 'color', 'size', 'product', 'sku')
    search_fields = ('product__title', 'color__title', 'size__title', 'sku')
    readonly_fields = ('image_tag',)
    list_editable = ('status', 'available_stock', 'image_id', 'color', 'size', 'sku')



# =========================================================
# ImageGallery ADMIN
# =========================================================
@admin.register(ImageGallery)
class ImageGalleryAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('id', 'product', 'image_tag', 'status')
    list_filter = ('status',)
    search_fields = ('product__title',)
    readonly_fields = ('image_tag',)



# =========================================================
# SLIDER ADMIN
# =========================================================
@admin.register(Slider)
class SliderAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('id', 'title', 'slider_type', 'product', 'status', 'image_tag')
    list_filter = ('status', 'slider_type')
    search_fields = ('title', 'sub_title', 'paragraph')
    readonly_fields = ('image_tag',)


# =========================================================
# REVIEW ADMIN
# =========================================================
@admin.register(Review)
class ReviewAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'subject', 'rating', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'rating')
    search_fields = ('subject', 'comment', 'user__username', 'product__title')
    readonly_fields = ('created_at', 'updated_at')


# =========================================================
# ACCEPTANCE PAYMENT ADMIN
# =========================================================
@admin.register(AcceptancePayment)
class AcceptancePaymentAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('id', 'title', 'sub_title', 'help_time', 'shop_amount', 'status', 'is_featured', 'image_tag')
    list_filter = ('status', 'is_featured')
    search_fields = ('title', 'sub_title')
    readonly_fields = ('image_tag',)
