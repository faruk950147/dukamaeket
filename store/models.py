from django.db import models
from django.utils.text import slugify
from django.utils.html import mark_safe
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Avg, Sum
from decimal import Decimal
from store.validators import validate_image_size

User = get_user_model()

# =========================================================
# HELPERS & MIXINS
# =========================================================
STATUS_CHOICES = (
    ('active', 'Active'),
    ('inactive', 'Inactive'),
)

SLIDER_TYPE_CHOICES = (
    ('none', 'None'),
    ('slider', 'Slider'),
    ('add', 'Add'),
    ('feature', 'Feature'),
    ('promotion', 'Promotion'),
)

def generate_unique_slug(cls, title: str) -> str:
    base_slug = slugify(title)
    slug = base_slug
    counter = 1
    while cls.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


class ImageTagMixin(models.Model):
    class Meta:
        abstract = True

    def image_tag(self):
        img = getattr(self, 'image', None)
        if img and hasattr(img, 'url'):
            return mark_safe(
                f'<img src="{img.url}" style="max-width:50px; border-radius:5px;" />'
            )
        return mark_safe('<span>No Image</span>')


# =========================================================
# 01. CATEGORY
# =========================================================
class Category(ImageTagMixin):
    parent = models.ForeignKey(
        'self', related_name='children',
        on_delete=models.CASCADE, null=True, blank=True
    )
    title = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True, null=True)
    image = models.ImageField(
        upload_to='categories/%Y/%m/%d/',
        default='defaults/default.jpg',
        validators=[validate_image_size]
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = '01. Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Category, self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# =========================================================
# 02. BRAND
# =========================================================
class Brand(ImageTagMixin):
    title = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True, null=True)
    image = models.ImageField(
        upload_to='brands/%Y/%m/%d/',
        default='defaults/default.jpg',
        validators=[validate_image_size]
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = '02. Brands'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Brand, self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# =========================================================
# 03. COLOR
# =========================================================
class Color(models.Model):
    title = models.CharField(max_length=20, unique=True)
    code = models.CharField(max_length=20, unique=True)

    class Meta:
        verbose_name_plural = '03. Product Colors'

    def color_tag(self):
        return mark_safe(
            f'<div style="width:20px; height:20px; background:{self.code}; border:1px solid #ddd;"></div>'
        )

    def __str__(self):
        return self.title


# =========================================================
# 04. SIZE
# =========================================================
class Size(models.Model):
    title = models.CharField(max_length=20, unique=True)
    code = models.CharField(max_length=10, unique=True)

    class Meta:
        verbose_name_plural = '04. Product Sizes'

    def __str__(self):
        return self.title


# =========================================================
# 05. PRODUCT
# =========================================================
class Product(ImageTagMixin):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, related_name='products', on_delete=models.CASCADE)
    title = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True, null=True)

    old_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('500000.00'))
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('400000.00'))
    discount_percent = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=20
    )

    available_stock = models.PositiveIntegerField(default=1)
    sold = models.PositiveIntegerField(default=0)

    short_des = models.TextField(default='N/A')
    long_des = models.TextField(default='N/A')

    deadline = models.DateTimeField(blank=True, null=True)
    is_deadline = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = '05. Products'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Product, self.title)

        self.sale_price = (
            self.old_price * (100 - self.discount_percent) / 100
        ).quantize(Decimal('0.01'))

        super().save(*args, **kwargs)

    def clean(self):
        if self.deadline and self.deadline < timezone.now():
            raise ValidationError("Deadline cannot be in the past.")

    @property
    def total_available_stock(self):
        variant_stock = self.variants.aggregate(
            Sum('available_stock')
        )['available_stock__sum'] or 0
        return self.available_stock + variant_stock

    @property
    def average_review(self):
        return float(self.reviews.filter(status='active').aggregate(Avg('rating'))['rating__avg'] or 0)

    @property
    def count_review(self):
        return self.reviews.filter(status='active').count()

    def __str__(self):
        return self.title


# =========================================================
# 06. PRODUCT VARIANT
# =========================================================
class ProductVariant(ImageTagMixin):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    color = models.ForeignKey(Color, null=True, blank=True, on_delete=models.SET_NULL)
    size = models.ForeignKey(Size, null=True, blank=True, on_delete=models.SET_NULL)

    sku = models.CharField(max_length=100, unique=True, blank=True)
    image = models.ImageField(
        upload_to='variants/%Y/%m/%d/',
        default='defaults/default.jpg',
        validators=[validate_image_size]
    )

    variant_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    available_stock = models.PositiveIntegerField(default=0)

    is_default = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = '06. Product Variants'
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'color', 'size'],
                name='unique_variant_item'
            )
        ]

    def save(self, *args, **kwargs):
        if not self.sku or ProductVariant.objects.filter(sku=self.sku).exclude(id=self.id).exists():
            base = self.product.slug[:5].upper()
            c = self.color.title[:2].upper() if self.color else "XX"
            s = self.size.code.upper() if self.size else "XX"

            base_sku = f"{base}-{c}-{s}"
            sku = base_sku
            counter = 1

            while ProductVariant.objects.filter(sku=sku).exclude(id=self.id).exists():
                sku = f"{base_sku}-{counter}"
                counter += 1

            self.sku = sku

        if self.is_default:
            ProductVariant.objects.filter(product=self.product).exclude(id=self.id).update(is_default=False)

        super().save(*args, **kwargs)

    @property
    def final_price(self):
        return self.variant_price if self.variant_price > 0 else self.product.sale_price

    def __str__(self):
        return f"{self.product.title} - {self.color} - {self.size}"


# =========================================================
# 07. IMAGE GALLERY
# =========================================================
class ImageGallery(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    variant = models.ForeignKey(
        ProductVariant, related_name='variant_images',
        on_delete=models.SET_NULL, null=True, blank=True
    )
    image = models.ImageField(
        upload_to='gallery/%Y/%m/%d/',
        default='defaults/default.jpg',
        validators=[validate_image_size]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = '07. Image Galleries'


# =========================================================
# 08. SLIDER
# =========================================================
class Slider(ImageTagMixin):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    slider_type = models.CharField(max_length=10, choices=SLIDER_TYPE_CHOICES, default='none')
    title = models.CharField(max_length=150, unique=True)
    sub_title = models.CharField(max_length=150, blank=True, null=True)
    paragraph = models.CharField(max_length=150, blank=True, null=True)
    image = models.ImageField(
        upload_to='sliders/%Y/%m/%d/',
        default='defaults/default.jpg',
        validators=[validate_image_size]
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '08. Sliders'

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


# =========================================================
# 09. REVIEW
# =========================================================
class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50)
    comment = models.TextField(max_length=500)
    rating = models.FloatField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '09. Reviews'
        constraints = [
            models.UniqueConstraint(fields=['product', 'user'], name='unique_review')
        ]


# =========================================================
# 10. ACCEPTANCE PAYMENT
# =========================================================
class AcceptancePayment(ImageTagMixin):
    title = models.CharField(max_length=150, unique=True)
    sub_title = models.CharField(max_length=150)
    image = models.ImageField(
        upload_to='acceptance_payments/%Y/%m/%d/',
        default='defaults/default.jpg',
        validators=[validate_image_size]
    )
    help_time = models.CharField(max_length=150, default='100')
    shop_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '10. Acceptance Payments'

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
