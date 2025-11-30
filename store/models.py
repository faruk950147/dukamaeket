from django.db import models
from django.utils.text import slugify
from django.utils.html import mark_safe
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Avg
from decimal import Decimal

User = get_user_model()

# =========================================================
# 01. CHOICES
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

# =========================================================
# 02. SLUG GENERATOR
# =========================================================
def generate_unique_slug(cls, title: str) -> str:
    base_slug = slugify(title)
    slug = base_slug
    counter = 1
    while cls.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug

# =========================================================
# 03. IMAGE TAG MIXIN
# =========================================================
class ImageTagMixin(models.Model):
    class Meta:
        abstract = True

    def image_tag(self):
        img = getattr(self, 'image', None)
        if img and hasattr(img, 'url'):
            return mark_safe(f'<img src="{img.url}" style="max-width:50px; max-height:50px;" />')
        return mark_safe('<span>No Image</span>')

# =========================================================
# 04. CATEGORY MODEL
# =========================================================
class Category(ImageTagMixin):
    parent = models.ForeignKey(
        'self', related_name='children', on_delete=models.CASCADE,
        null=True, blank=True
    )
    title = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True, db_index=True, blank=True, null=True)

    keyword = models.CharField(max_length=150, default='N/A')
    description = models.CharField(max_length=150, default='N/A')

    image = models.ImageField(upload_to='categories/%Y/%m/%d/', default='defaults/default.jpg')

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    is_featured = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '01. Categories'

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.slug:
            self.slug = generate_unique_slug(Category, self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

# =========================================================
# 05. BRAND MODEL
# =========================================================
class Brand(ImageTagMixin):
    title = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True, db_index=True, blank=True, null=True)

    keyword = models.CharField(max_length=150, default='N/A')
    description = models.CharField(max_length=150, default='N/A')

    image = models.ImageField(upload_to='brands/%Y/%m/%d/', default='defaults/default.jpg')

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    is_featured = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '02. Brands'

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.slug:
            self.slug = generate_unique_slug(Brand, self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

# =========================================================
# 06. PRODUCT MODEL
# =========================================================
class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, related_name='products', on_delete=models.CASCADE)
    title = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True, db_index=True, blank=True, null=True)

    old_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('500000.00'))
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('400000.00'))

    available_stock = models.PositiveIntegerField(validators=[MaxValueValidator(10000)], default=1)
    discount_percent = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], default=20)

    prev_des = models.TextField(default='N/A')
    add_des = models.TextField(default='N/A')
    short_des = models.TextField(default='N/A')
    long_des = models.TextField(default='N/A')
    keyword = models.TextField(default='N/A')
    description = models.TextField(default='N/A')
    tag = models.CharField(max_length=150, default='N/A')

    deadline = models.DateTimeField(blank=True, null=True)
    is_deadline = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    sold = models.PositiveIntegerField(default=0)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '03. Products'

    def save(self, *args, **kwargs):
        self.sale_price = (
            (self.old_price * (Decimal(100) - Decimal(self.discount_percent)) / Decimal(100))
            .quantize(Decimal('0.01'))
        )

        self.full_clean()
        if not self.slug:
            self.slug = generate_unique_slug(Product, self.title)

        super().save(*args, **kwargs)

    def clean(self):
        if self.deadline and self.deadline < timezone.now():
            raise ValidationError("Deadline cannot be in the past.")

    @property
    def remaining_seconds(self):
        if self.deadline and self.is_deadline:
            now = timezone.now()
            remaining = self.deadline - now
            return max(0, int(remaining.total_seconds()))
        return 0

    @property
    def average_review(self):
        return float(self.reviews.filter(status='active').aggregate(Avg('rating'))['rating__avg'] or 0)

    @property
    def count_review(self):
        return self.reviews.filter(status='active').count()

    @property
    def sold_percentage(self):
        total = self.sold + self.available_stock
        if total > 0:
            return round((self.sold / total) * 100, 2)
        return 0

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

# =========================================================
# 07. IMAGE GALLERY MODEL
# =========================================================
class ImageGallery(ImageTagMixin):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='galleries/%Y/%m/%d/', default='defaults/default.jpg')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '04. Image Galleries'

    def __str__(self):
        return f"{self.product.title} Image"

# =========================================================
# 08. COLOR MODEL
# =========================================================
class Color(ImageTagMixin):
    title = models.CharField(max_length=20, unique=True)
    code = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '05. Product Colors'

    def __str__(self):
        return f"{self.title} ({self.code})"

    @property
    def color_tag(self):
        if self.code:
            return mark_safe(
                f'<div style="width:30px; height:30px; background-color:{self.code}; border:1px solid #000;"></div>'
            )
        return ""

# =========================================================
# 09. SIZE MODEL
# =========================================================
class Size(models.Model):
    title = models.CharField(max_length=20, unique=True)
    code = models.CharField(max_length=10, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '06. Product Sizes'

    def __str__(self):
        return f"{self.title} ({self.code})"

# =========================================================
# 10. PRODUCT VARIANT MODEL
# =========================================================
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    color = models.ForeignKey(Color, blank=True, null=True, on_delete=models.SET_NULL)
    size = models.ForeignKey(Size, blank=True, null=True, on_delete=models.SET_NULL)
    image = models.ImageField(upload_to='colors/%Y/%m/%d/', default='defaults/default.jpg')
    variant_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    available_stock = models.PositiveIntegerField(default=0)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = '07. Product Variants'
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'color', 'size'],
                name='unique_variant'
            )
        ]

    def __str__(self):
        return f"{self.product.title} - {self.size or 'No Size'} - {self.color or 'No Color'}"

# =========================================================
# 11. SLIDER MODEL
# =========================================================
class Slider(ImageTagMixin):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    slider_type = models.CharField(max_length=10, choices=SLIDER_TYPE_CHOICES, default='none')
    title = models.CharField(max_length=150, unique=True)
    sub_title = models.CharField(max_length=150, blank=True, null=True)
    paragraph = models.CharField(max_length=150, blank=True, null=True)
    image = models.ImageField(upload_to='sliders/%Y/%m/%d/', default='defaults/default.jpg')

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '08. Sliders'

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

# =========================================================
# 12. REVIEW MODEL
# =========================================================
class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    subject = models.CharField(max_length=50)
    comment = models.CharField(max_length=500)
    rating = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '09. Reviews'

    def __str__(self):
        return self.subject or f"Review by {self.user.username}"

# =========================================================
# 13. ACCEPTANCE PAYMENT MODEL
# =========================================================
class AcceptancePayment(ImageTagMixin):
    title = models.CharField(max_length=150, unique=True)
    sub_title = models.CharField(max_length=150)

    image = models.ImageField(upload_to='acceptance_payments/%Y/%m/%d/', default='defaults/default.jpg')
    help_time = models.PositiveIntegerField(default=100)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    is_featured = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '10. Acceptance Payments'

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
