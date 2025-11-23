from django.db import models
from django.utils.text import slugify
from django.utils.html import mark_safe
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Avg

User = get_user_model()


# ---------------- STATUS CHOICES ----------------
class StatusChoices(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    INACTIVE = 'INACTIVE', 'Inactive'


# ---------------- HELPER FUNCTION ----------------
def generate_unique_slug(model_class, title):
    base_slug = slugify(title)
    slug = base_slug
    counter = 1
    while model_class.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


# ---------------- CATEGORY ----------------
class Category(models.Model):
    parent = models.ForeignKey('self', related_name='children', on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True, null=True, blank=True)
    keyword = models.CharField(max_length=150, default='N/A', null=True, blank=True)
    description = models.CharField(max_length=150, default='N/A', null=True, blank=True)
    image = models.ImageField(upload_to='categories/%Y/%m/%d/')
    status = models.CharField(max_length=8, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '01. Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Category, self.title)
        super().save(*args, **kwargs)

    @property
    def image_tag(self):
        if self.image and hasattr(self.image, 'url'):
            return mark_safe(f'<img src="{self.image.url}" alt="{self.title}" style="max-width:100px; max-height:100px;"/>')
        return mark_safe('<span>No Image Available</span>')

    def __str__(self):
        title = getattr(self, 'title', 'Unknown Category')
        status = getattr(self, 'status', 'INACTIVE')
        return f"{title} - {self.get_status_display() if hasattr(self, 'get_status_display') else status}"


# ---------------- CATEGORY TRANSLATION ----------------
class CategoryTranslation(models.Model):
    LANGUAGE_CHOICES = [('en', 'English'), ('bn', 'Bangla')]

    category = models.ForeignKey(Category, related_name='translations', on_delete=models.CASCADE)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    title = models.CharField(max_length=150)
    keyword = models.CharField(max_length=150, null=True, blank=True)
    description = models.CharField(max_length=150, null=True, blank=True)

    class Meta:
        unique_together = ('category', 'language')
        verbose_name_plural = "Category Translations"

    def __str__(self):
        category_title = getattr(self.category, 'title', 'Unknown Category')
        language = getattr(self, 'language', 'en')
        return f"{category_title} ({language})"


# ---------------- BRAND ----------------
class Brand(models.Model):
    title = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True, null=True, blank=True)
    keyword = models.CharField(max_length=150, default='N/A', null=True, blank=True)
    description = models.CharField(max_length=150, default='N/A', null=True, blank=True)
    image = models.ImageField(upload_to='brands/%Y/%m/%d/')
    status = models.CharField(max_length=8, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '02. Brands'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Brand, self.title)
        super().save(*args, **kwargs)

    @property
    def image_tag(self):
        if self.image and hasattr(self.image, 'url'):
            return mark_safe(f'<img src="{self.image.url}" alt="{self.title}" style="max-width:50px; max-height:50px;"/>')
        return mark_safe('<span>No Image Available</span>')

    def __str__(self):
        title = getattr(self, 'title', 'Unknown Brand')
        status = getattr(self, 'status', 'INACTIVE')
        return f"{title} - {self.get_status_display() if hasattr(self, 'get_status_display') else status}"


# ---------------- BRAND TRANSLATION ----------------
class BrandTranslation(models.Model):
    LANGUAGE_CHOICES = [('en', 'English'), ('bn', 'Bangla')]

    brand = models.ForeignKey(Brand, related_name='translations', on_delete=models.CASCADE)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    title = models.CharField(max_length=150)
    keyword = models.CharField(max_length=150, null=True, blank=True)
    description = models.CharField(max_length=150, null=True, blank=True)

    class Meta:
        unique_together = ('brand', 'language')
        verbose_name_plural = "Brand Translations"

    def __str__(self):
        brand_title = getattr(self.brand, 'title', 'Unknown Brand')
        language = getattr(self, 'language', 'en')
        return f"{brand_title} ({language})"


# ---------------- PRODUCT ----------------
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    title = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True, null=True, blank=True)
    old_price = models.DecimalField(decimal_places=2, max_digits=10, default=1000.00)
    sale_price = models.DecimalField(decimal_places=2, max_digits=10, default=500.00)
    available_stock = models.PositiveIntegerField(validators=[MaxValueValidator(1000)], default=0)
    discount_percent = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], default=0)
    keyword = models.TextField(default='N/A', null=True, blank=True)
    description = models.TextField(default='N/A', null=True, blank=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d/')
    offers_deadline = models.DateTimeField(blank=True, null=True)
    is_timeline = models.CharField(max_length=8, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)
    status = models.CharField(max_length=8, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '03. Products'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Product, self.title)
        super().save(*args, **kwargs)

    def clean(self):
        if self.sale_price > self.old_price:
            raise ValidationError("Sale price cannot be greater than old price.")
        if self.discount_percent > 0:
            calculated_price = self.old_price - (self.old_price * self.discount_percent / 100)
            if round(calculated_price, 2) != round(self.sale_price, 2):
                raise ValidationError("Sale price does not match discount percent.")
        if self.offers_deadline and self.offers_deadline < timezone.now():
            raise ValidationError("Offer deadline cannot be in the past.")

    @property
    def image_tag(self):
        if self.image and hasattr(self.image, 'url'):
            return mark_safe(f'<img src="{self.image.url}" alt="{self.title}" style="max-width:50px; max-height:50px;"/>')
        return mark_safe('<span>No Image Available</span>')

    @property
    def offers_remaining(self):
        if self.offers_deadline and self.is_timeline == StatusChoices.ACTIVE:
            remaining = self.offers_deadline - timezone.now()
            return max(0, int(remaining.total_seconds()))
        return 0

    @property    
    def average_review(self):
        reviews = Review.objects.filter(product=self, status=StatusChoices.ACTIVE).aggregate(average=Avg('rate'))
        return float(reviews["average"] or 0)
    
    @property
    def count_review(self):
        return Review.objects.filter(product=self, status=StatusChoices.ACTIVE).count()

    def __str__(self):
        title = getattr(self, 'title', 'Unknown Product')
        status = getattr(self, 'status', 'INACTIVE')
        return f"{title} - {self.get_status_display() if hasattr(self, 'get_status_display') else status}"


# ---------------- PRODUCT TRANSLATION ----------------
class ProductTranslation(models.Model):
    LANGUAGE_CHOICES = [('en', 'English'), ('bn', 'Bangla')]

    product = models.ForeignKey(Product, related_name='translations', on_delete=models.CASCADE)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    title = models.CharField(max_length=150)
    keyword = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('product', 'language')
        verbose_name_plural = "Product Translations"

    def __str__(self):
        product_title = getattr(self.product, 'title', 'Unknown Product')
        language = getattr(self, 'language', 'en')
        return f"{product_title} ({language})"


# ---------------- COLOR ----------------
class Color(models.Model):
    title = models.CharField(max_length=20, unique=True)
    code = models.CharField(max_length=20, unique=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '05. Product Colors'
    
    @property
    def color_tag(self):
        if self.code:
            return mark_safe(f'<div style="width:30px; height:30px; background-color:{self.code}; border:1px solid #000;"></div>')
        return ""
    
    def __str__(self):
        title = getattr(self, 'title', 'Unknown Color')
        code = getattr(self, 'code', '')
        return f"{title} ({code})" if code else title


# ---------------- COLOR TRANSLATION ----------------
class ColorTranslation(models.Model):
    LANGUAGE_CHOICES = [('en', 'English'), ('bn', 'Bangla')]
    color = models.ForeignKey(Color, related_name='translations', on_delete=models.CASCADE)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    title = models.CharField(max_length=20)

    class Meta:
        unique_together = ('color', 'language')
        verbose_name_plural = "Color Translations"

    def __str__(self):
        color_title = getattr(self.color, 'title', 'Unknown Color')
        language = getattr(self, 'language', 'en')
        return f"{color_title} ({language})"


# ---------------- SIZE ----------------
class Size(models.Model):
    title = models.CharField(max_length=20, unique=True)
    code = models.CharField(max_length=10, unique=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)   

    class Meta:
        ordering = ['id']
        verbose_name_plural = '06. Product Sizes'

    def __str__(self):
        title = getattr(self, 'title', 'Unknown Size')
        code = getattr(self, 'code', '')
        return f"{title} ({code})" if code else title


# ---------------- SIZE TRANSLATION ----------------
class SizeTranslation(models.Model):
    LANGUAGE_CHOICES = [('en', 'English'), ('bn', 'Bangla')]
    size = models.ForeignKey(Size, related_name='translations', on_delete=models.CASCADE)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    title = models.CharField(max_length=20)

    class Meta:
        unique_together = ('size', 'language')
        verbose_name_plural = "Size Translations"

    def __str__(self):
        size_title = getattr(self.size, 'title', 'Unknown Size')
        language = getattr(self, 'language', 'en')
        return f"{size_title} ({language})"


# ---------------- SLIDER ----------------
class Slider(models.Model):
    title = models.CharField(max_length=150, unique=True)
    image = models.ImageField(upload_to='sliders/%Y/%m/%d/')
    status = models.CharField(max_length=8, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '04. Sliders'

    @property
    def image_tag(self):
        if self.image and hasattr(self.image, 'url'):
            return mark_safe(f'<img src="{self.image.url}" alt="{self.title}" style="max-width:100px; max-height:50px;"/>')
        return mark_safe('<span>No Image Available</span>')

    def __str__(self):
        title = getattr(self, 'title', 'Unknown Slider')
        status = getattr(self, 'status', 'INACTIVE')
        return f"{title} - {self.get_status_display() if hasattr(self, 'get_status_display') else status}"


# ---------------- REVIEW ----------------
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    rate = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])
    status = models.CharField(max_length=8, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '11. Reviews'

    def __str__(self):
        if self.subject and self.subject.strip():
            return self.subject
        user_name = getattr(self.user, 'username', 'Unknown User')
        product_title = getattr(self.product, 'title', 'Unknown Product')
        return f"Review by {user_name} on {product_title}"
