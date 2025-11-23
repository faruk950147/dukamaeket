from django.contrib import admin
from store.models import (
    Category, CategoryTranslation,
    Brand, BrandTranslation,
    Product, ProductTranslation,
    Color, ColorTranslation,
    Size, SizeTranslation,
    Slider, SliderTranslation,
    Review, ReviewTranslation,
    ImageGallery
)

# ---------------- CATEGORY ADMIN ----------------
class CategoryTranslationInline(admin.TabularInline):
    model = CategoryTranslation
    extra = 1
    fields = ('language', 'title', 'keyword', 'description')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_date', 'updated_date', 'image_tag')
    list_filter = ('status', 'created_date')
    search_fields = ('title', 'keyword', 'description')
    readonly_fields = ('image_tag',)
    inlines = [CategoryTranslationInline]
    prepopulated_fields = {"slug": ("title",)}

# ---------------- BRAND ADMIN ----------------
class BrandTranslationInline(admin.TabularInline):
    model = BrandTranslation
    extra = 1
    fields = ('language', 'title', 'keyword', 'description')

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_date', 'updated_date', 'image_tag')
    list_filter = ('status', 'created_date')
    search_fields = ('title', 'keyword', 'description')
    readonly_fields = ('image_tag',)
    inlines = [BrandTranslationInline]
    prepopulated_fields = {"slug": ("title",)}

# ---------------- PRODUCT ADMIN ----------------
class ProductTranslationInline(admin.TabularInline):
    model = ProductTranslation
    extra = 1
    fields = ('language', 'title', 'keyword', 'description')

class ImageGalleryInline(admin.TabularInline):
    model = ImageGallery
    extra = 0
    readonly_fields = ('image_tag',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'brand', 'sale_price', 'old_price', 'discount_percent', 'available_stock', 'status', 'remaining', 'average_review', 'count_review', 'image_tag')
    list_filter = ('status', 'category', 'brand', 'created_date')
    search_fields = ('title', 'keyword', 'description')
    readonly_fields = ('image_tag', 'remaining', 'average_review', 'count_review')
    inlines = [ProductTranslationInline, ImageGalleryInline]
    prepopulated_fields = {"slug": ("title",)}

# ---------------- IMAGE GALLERY ADMIN ----------------
@admin.register(ImageGallery)
class ImageGalleryAdmin(admin.ModelAdmin):
    list_display = ('product', 'image_tag', 'created_date')
    readonly_fields = ('image_tag',)

# ---------------- COLOR ADMIN ----------------
class ColorTranslationInline(admin.TabularInline):
    model = ColorTranslation
    extra = 1

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'color_tag', 'created_date')
    search_fields = ('title', 'code')
    readonly_fields = ('color_tag',)
    inlines = [ColorTranslationInline]

# ---------------- SIZE ADMIN ----------------
class SizeTranslationInline(admin.TabularInline):
    model = SizeTranslation
    extra = 1

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'created_date')
    search_fields = ('title', 'code')
    inlines = [SizeTranslationInline]

# ---------------- SLIDER ADMIN ----------------
class SliderTranslationInline(admin.TabularInline):
    model = SliderTranslation
    extra = 1

@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_date', 'image_tag')
    list_filter = ('status', 'created_date')
    readonly_fields = ('image_tag',)
    inlines = [SliderTranslationInline]

# ---------------- REVIEW ADMIN ----------------
class ReviewTranslationInline(admin.TabularInline):
    model = ReviewTranslation
    extra = 1

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('subject', 'product', 'user', 'rate', 'status', 'created_date')
    list_filter = ('status', 'rate', 'created_date')
    search_fields = ('subject', 'comment', 'user__username', 'product__title')
    inlines = [ReviewTranslationInline]
