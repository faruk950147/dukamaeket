from django.contrib import admin
from store.models import (
    Category, Brand, Color, Size,
    Product, ProductVariant, ImageGallery,
    Slider, Review, AcceptancePayment
)
# Registering Category model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'parent', 'title', 'image_tag', 'status', 
                    'is_featured', 'created_at', 'updated_at']
    list_editable = ['is_featured', 'status']
    list_filter = ['status']
    search_fields = ['title']
    
# Registering Brand model
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'image_tag', 'status', 
                    'is_featured', 'created_at', 'updated_at']
    list_editable = ['is_featured', 'status']
    list_filter = ['status']
    search_fields = ['title']

# Registering Color model
@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'code', 'color_tag']
    search_fields = ['title']   
    
# Registering Size model
@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'code']
    search_fields = ['title']

# Variant inline for displaying variants within product admin
class VariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['color', 'size', 'sku', 'variant_price', 'available_stock', 'is_default', 'image_tag']
    readonly_fields = ['image_tag']

# Gallery inline for displaying image galleries within product admin
class GalleryInline(admin.TabularInline):
    model = ImageGallery
    extra = 3
    fields = ['variant', 'image']

# Product admin configuration
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'brand', 'title', 'slug', 'old_price', 'sale_price', 
                    'discount_percent', 'available_stock', 'sold', 'status', 'is_featured', 'created_at', 'updated_at']
    list_filter = ['category', 'brand', 'status', 'is_featured']
    search_fields = ['title', 'slug', 'variants__sku']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [VariantInline, GalleryInline]
    
    fieldsets = (
        ('Basic Info', {'fields': ('category', 'brand', 'title', 'slug', 'status', 'is_featured')}),
        ('Pricing', {'fields': ('old_price', 'discount_percent', 'sale_price')}),
        ('Stock & Sales', {'fields': ('available_stock', 'sold')}),
        ('Description', {'fields': ('short_des', 'long_des', 'prev_des', 'add_des', 'tag')}),
        ('SEO & Flash Sale', {'fields': ('keyword', 'description', 'deadline', 'is_deadline')}),
    )
    readonly_fields = ['sale_price']

# Registering ProductVariant model
@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'color', 'size', 'sku', 'variant_price', 'available_stock', 'is_default', 'image_tag', 'created_at', 'updated_at']
    list_filter = ['product', 'color', 'size']
    search_fields = ['sku', 'product__title']
    
# Registering ImageGallery model
@admin.register(ImageGallery)
class ImageGalleryAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'variant', 'image']
    list_filter = ['product']
    search_fields = ['product__title', 'variant__sku']
    
# Registering Slider model
@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'image_tag', 'status', 'created_at', 'updated_at']
    list_editable = ['status']
    list_filter = ['status']
    search_fields = ['title']
    
# Registering Review model
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'user', 'rating', 'status', 'created_at', 'updated_at']
    list_editable = ['status']
    list_filter = ['status', 'rating']
    search_fields = ['product__title', 'user__username']
    
    
# Registering AcceptancePayment model
@admin.register(AcceptancePayment)
class AcceptancePaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'sub_title', 'help_time', 'shop_amount', 'status', 'is_featured', 'image_tag', 'created_at', 'updated_at']
    list_editable = ['status']
    list_filter = ['status']
    search_fields = ['method_name']