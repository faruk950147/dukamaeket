from django.contrib import admin
from store.models import (
    Category, Brand, Product, ImageGallery,
    Color, ProductVariant, Size, Slider, Review,
)


# ===================================================================
# CATEGORY ADMIN
# ===================================================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'parent', 'status', 'image_tag')
    list_editable = ('status',)
    search_fields = ('title',)
    list_filter = ('status', 'parent')
    readonly_fields = ('image_tag',)

    prepopulated_fields = {'slug': ('title',)}  # slug auto fill


# ===================================================================
# BRAND ADMIN
# ===================================================================
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'image_tag')
    list_editable = ('status',)
    search_fields = ('title',)
    list_filter = ('status',)
    readonly_fields = ('image_tag',)

    prepopulated_fields = {'slug': ('title',)}


# ===================================================================
# IMAGE GALLERY INLINE 
# ===================================================================
class ImageGalleryInline(admin.TabularInline):
    model = ImageGallery
    extra = 1
    readonly_fields = ('image_tag',)


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    readonly_fields = ('image_tag',)

# ===================================================================
# PRODUCT ADMIN
# ===================================================================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'category', 'brand',
        'old_price', 'sale_price',
        'discount_percent', 'available_stock',
        'status', 'image_tag'
    )
    list_editable = ('status',)
    search_fields = ('title', 'keyword')
    list_filter = ('category', 'brand', 'status')
    readonly_fields = ('image_tag', 'average_review', 'count_review')

    prepopulated_fields = {'slug': ('title',)}

    inlines = [ImageGalleryInline, ProductVariantInline]   # gallery inline added


# ===================================================================
# COLOR ADMIN
# ===================================================================
@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'code', 'color_tag')
    readonly_fields = ('color_tag',)
    search_fields = ('title', 'code')


# ===================================================================
# SIZE ADMIN
# ===================================================================
@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'code')
    search_fields = ('title', 'code')


# ===================================================================
# SLIDER ADMIN
# ===================================================================
@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'image_tag')
    list_editable = ('status',)
    readonly_fields = ('image_tag',)
    search_fields = ('title',)
    list_filter = ('status',)


# ===================================================================
# REVIEW ADMIN
# ===================================================================
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'rate', 'status', 'created_date')
    list_editable = ('status',)
    search_fields = ('product__title', 'user__username')
    list_filter = ('status', 'rate', 'created_date')

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'color', 'size', 'price', 'stock', 'status')
    list_editable = ('status',)
    search_fields = ('product__title', 'color__title', 'size__title')
    list_filter = ('status', 'color', 'size')