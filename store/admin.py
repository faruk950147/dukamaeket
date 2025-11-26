from django.contrib import admin
from store.models import (
    Category, Brand, Product, ImageGallery, Color, Size,
    ProductVariant, Slider, Review, Advancement, AcceptancePayment
)

# =========================================================
# 01. CATEGORY ADMIN
# =========================================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'parent', 'slug', 'keyword', 'description', 'status', 'created_date', 'updated_date', 'image_tag')
    list_filter = ('status', 'parent')
    search_fields = ('title', 'slug', 'keyword', 'description')
    readonly_fields = ('id', 'image_tag', 'created_date', 'updated_date')
    fields = ('parent', 'title', 'slug', 'keyword', 'description', 'image', 'image_tag', 'status')

# =========================================================
# 02. BRAND ADMIN
# =========================================================
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'slug', 'keyword', 'description', 'status', 'created_date', 'updated_date', 'image_tag')
    list_filter = ('status',)
    search_fields = ('title', 'slug', 'keyword', 'description')
    readonly_fields = ('id', 'image_tag', 'created_date', 'updated_date')
    fields = ('title', 'slug', 'keyword', 'description', 'image', 'image_tag', 'status')

# =========================================================
# 03. IMAGE GALLERY INLINE
# =========================================================
class ImageGalleryInline(admin.TabularInline):
    model = ImageGallery
    extra = 1
    readonly_fields = ('image_tag', 'created_date', 'updated_date')
    fields = ('image', 'image_tag', 'created_date', 'updated_date')

# =========================================================
# 04. PRODUCT VARIANT INLINE
# =========================================================
class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    readonly_fields = ('image_tag', 'created_date', 'updated_date')
    fields = ('color', 'size', 'variant_price', 'available_stock', 'status', 'image_tag', 'created_date', 'updated_date')

# =========================================================
# 05. ADVANCEMENT INLINE
# =========================================================
class AdvancementInline(admin.TabularInline):
    model = Advancement
    extra = 1
    readonly_fields = ('image_tag', 'created_date', 'updated_date')
    fields = ('advancement_type', 'product', 'title', 'subtitle', 'image', 'image_tag', 'status', 'created_date', 'updated_date')

# =========================================================
# 06. PRODUCT ADMIN
# =========================================================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'slug', 'category', 'brand', 'old_price', 'sale_price', 'discount_percent', 'available_stock', 'is_deadline', 'is_featured', 'status', 'created_date', 'updated_date', 'image_tag')
    list_filter = ('status', 'category', 'brand', 'is_deadline', 'is_featured')
    search_fields = ('title', 'slug', 'keyword', 'description')
    readonly_fields = ('id', 'image_tag', 'created_date', 'updated_date')
    inlines = [ImageGalleryInline, ProductVariantInline, AdvancementInline]
    fields = ('category', 'brand', 'title', 'slug', 'old_price', 'sale_price', 'discount_percent', 'available_stock', 'keyword', 'description', 'image', 'image_tag', 'deadline', 'is_deadline', 'is_featured', 'status')

# =========================================================
# 07. COLOR ADMIN
# =========================================================
@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'code', 'color_tag', 'created_date', 'updated_date', 'image_tag')
    search_fields = ('title', 'code')
    readonly_fields = ('id', 'color_tag', 'image_tag', 'created_date', 'updated_date')
    fields = ('title', 'code', 'image', 'image_tag')

# =========================================================
# 08. SIZE ADMIN
# =========================================================
@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'code', 'created_date', 'updated_date')
    search_fields = ('title', 'code')
    readonly_fields = ('id', 'created_date', 'updated_date')
    fields = ('title', 'code')

# =========================================================
# 09. SLIDER ADMIN
# =========================================================
@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'product', 'status', 'created_date', 'updated_date', 'image_tag')
    list_filter = ('status',)
    search_fields = ('title',)
    readonly_fields = ('id', 'image_tag', 'created_date', 'updated_date')
    fields = ('product', 'title', 'image', 'image_tag', 'status')

# =========================================================
# 10. REVIEW ADMIN
# =========================================================
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'subject', 'comment', 'rate', 'status', 'created_date', 'updated_date')
    list_filter = ('status', 'rate')
    search_fields = ('subject', 'comment', 'user__username', 'product__title')
    readonly_fields = ('id', 'created_date', 'updated_date')
    fields = ('product', 'user', 'subject', 'comment', 'rate', 'status')

# =========================================================
# 11. ADVANCEMENT ADMIN
# =========================================================
@admin.register(Advancement)
class AdvancementAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'advancement_type', 'product', 'status', 'created_date', 'updated_date', 'image_tag')
    list_filter = ('status', 'advancement_type')
    search_fields = ('title', 'subtitle')
    readonly_fields = ('id', 'image_tag', 'created_date', 'updated_date')
    fields = ('advancement_type', 'product', 'title', 'subtitle', 'image', 'image_tag', 'status')

# =========================================================
# 12. ACCEPTANCE PAYMENT ADMIN
# =========================================================
@admin.register(AcceptancePayment)
class AcceptancePaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'subtitle', 'amount', 'status', 'created_date', 'updated_date', 'image_tag')
    list_filter = ('status',)
    search_fields = ('title', 'subtitle')
    readonly_fields = ('id', 'image_tag', 'created_date', 'updated_date')
    fields = ('title', 'subtitle', 'image', 'image_tag', 'amount', 'status')
