from django.contrib import admin
from store.models import (
    Category, CategoryTranslation,
    Brand, BrandTranslation,
    Product, ProductTranslation,
    Color, ColorTranslation,
    Size, SizeTranslation,
    Slider,
    Review
)

# ---------------- CATEGORY ----------------
class CategoryTranslationInline(admin.TabularInline):
    model = CategoryTranslation
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'image_tag', 'created_date')
    search_fields = ('title',)
    list_filter = ('status',)
    inlines = [CategoryTranslationInline]


# ---------------- BRAND ----------------
class BrandTranslationInline(admin.TabularInline):
    model = BrandTranslation
    extra = 1

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'image_tag', 'created_date')
    search_fields = ('title',)
    list_filter = ('status',)
    inlines = [BrandTranslationInline]


# ---------------- PRODUCT ----------------
class ProductTranslationInline(admin.TabularInline):
    model = ProductTranslation
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'brand', 'status', 'sale_price', 'available_stock', 'image_tag')
    search_fields = ('title', 'category__title', 'brand__title')
    list_filter = ('status', 'is_timeline', 'category', 'brand')
    inlines = [ProductTranslationInline]


# ---------------- COLOR ----------------
class ColorTranslationInline(admin.TabularInline):
    model = ColorTranslation
    extra = 1

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'color_tag', 'created_date')
    search_fields = ('title', 'code')
    inlines = [ColorTranslationInline]


# ---------------- SIZE ----------------
class SizeTranslationInline(admin.TabularInline):
    model = SizeTranslation
    extra = 1

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'created_date')
    search_fields = ('title', 'code')
    inlines = [SizeTranslationInline]


# ---------------- SLIDER ----------------
@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'image_tag', 'created_date')
    search_fields = ('title',)
    list_filter = ('status',)


# ---------------- REVIEW ----------------
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('subject', 'product', 'user', 'rate', 'status', 'created_date')
    search_fields = ('subject', 'product__title', 'user__username')
    list_filter = ('status', 'rate', 'created_date')
