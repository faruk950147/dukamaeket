from django.contrib import admin
from .models import (
    Category, Brand, Product, ImageGallery, Color, Size, ProductVariant,
    Slider, Review, Advancement, AcceptancePayment
)

# =========================================================
# 01. CATEGORY ADMIN
# =========================================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'parent', 'status', 'created_date', 'updated_date', 'image_tag')
    list_filter = ('status',)
    search_fields = ('title', 'keyword', 'description')
    prepopulated_fields = {'slug': ('title',)}

# =========================================================
# 02. BRAND ADMIN
# =========================================================
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_date', 'updated_date', 'image_tag')
    list_filter = ('status',)
    search_fields = ('title', 'keyword', 'description')
    prepopulated_fields = {'slug': ('title',)}

# =========================================================
# 03. PRODUCT ADMIN
# =========================================================
class ImageGalleryInline(admin.TabularInline):
    model = ImageGallery
    extra = 1
    readonly_fields = ('image_tag',)

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    readonly_fields = ('image_tag',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'brand', 'sale_price', 'old_price', 'status', 'remaining', 'image_tag')
    list_filter = ('status', 'category', 'brand', 'is_deadline', 'is_featured')
    search_fields = ('title', 'keyword', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ImageGalleryInline, ProductVariantInline]

# =========================================================
# 04. IMAGE GALLERY ADMIN
# =========================================================
@admin.register(ImageGallery)
class ImageGalleryAdmin(admin.ModelAdmin):
    list_display = ('product', 'image_tag', 'created_date')
    readonly_fields = ('image_tag',)

# =========================================================
# 05. COLOR ADMIN
# =========================================================
@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'color_tag', 'image_tag', 'created_date')
    readonly_fields = ('color_tag', 'image_tag')

# =========================================================
# 06. SIZE ADMIN
# =========================================================
@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'created_date')

# =========================================================
# 07. PRODUCT VARIANT ADMIN
# =========================================================
@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'color', 'variant_price', 'available_stock', 'status', 'image_tag')
    list_filter = ('status',)
    readonly_fields = ('image_tag',)

# =========================================================
# 08. SLIDER ADMIN
# =========================================================
@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'product', 'status', 'image_tag')
    list_filter = ('status',)
    readonly_fields = ('image_tag',)

# =========================================================
# 09. REVIEW ADMIN
# =========================================================
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('subject', 'product', 'user', 'rate', 'status', 'created_date')
    list_filter = ('status', 'rate')
    search_fields = ('subject', 'comment', 'user__username', 'product__title')

# =========================================================
# 10. ADVANCEMENT ADMIN
# =========================================================
@admin.register(Advancement)
class AdvancementAdmin(admin.ModelAdmin):
    list_display = ('title', 'advancement_type', 'product', 'status', 'image_tag')
    list_filter = ('status', 'advancement_type')
    readonly_fields = ('image_tag',)

# =========================================================
# 11. ACCEPTANCE PAYMENT ADMIN
# =========================================================
@admin.register(AcceptancePayment)
class AcceptancePaymentAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'status', 'image_tag', 'created_date', 'updated_date')
    list_filter = ('status',)
    readonly_fields = ('image_tag',)
