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

ADVANCEMENT_TYPE_CHOICES = (
    ('banner', 'Banner'),
    ('feature', 'Feature'),
    ('promotion', 'Promotion'),
)

# =========================================================
# 02. HELPER FUNCTIONS
# =========================================================
def generate_unique_slug(model_class, title: str) -> str:
    base_slug = slugify(title)
    slug = base_slug
    counter = 1
    while model_class.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug

# =========================================================
# 03. IMAGE TAG MIXIN (Admin Preview)
# =========================================================
class ImageTagMixin(models.Model):
    class Meta:
        abstract = True

    def image_tag(self) -> str:
        img = getattr(self, 'image', None)
        if img and hasattr(img, 'url'):
            return mark_safe(f'<img src="{img.url}" style="max-width:50px; max-height:50px;" />')
        return mark_safe('<span>No Image</span>')

# =========================================================
# 04. CATEGORY MODEL
# =========================================================
class Category(ImageTagMixin):
    parent: models.ForeignKey = models.ForeignKey(
        'self', related_name='children', on_delete=models.CASCADE,
        null=True, blank=True
    )
    title: models.CharField = models.CharField(max_length=150, unique=True)
    slug: models.SlugField = models.SlugField(max_length=150, unique=True, blank=True)
    keyword: models.CharField = models.CharField(max_length=150, default='N/A')
    description: models.CharField = models.CharField(max_length=150, default='N/A')
    image: models.ImageField = models.ImageField(upload_to='categories/%Y/%m/%d/', default='defaults/default.jpg')
    status: models.CharField = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')
    created_date: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_date: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '01. Categories'

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        if not self.slug:
            self.slug = generate_unique_slug(Category, self.title)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.title} ({self.get_status_display()})"

# =========================================================
# 05. BRAND MODEL
# =========================================================
class Brand(ImageTagMixin):
    title: models.CharField = models.CharField(max_length=150, unique=True)
    slug: models.SlugField = models.SlugField(max_length=150, unique=True, blank=True)
    keyword: models.CharField = models.CharField(max_length=150, default='N/A')
    description: models.CharField = models.CharField(max_length=150, default='N/A')
    image: models.ImageField = models.ImageField(upload_to='brands/%Y/%m/%d/', default='defaults/default.jpg')
    status: models.CharField = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')
    created_date: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_date: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '02. Brands'

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        if not self.slug:
            self.slug = generate_unique_slug(Brand, self.title)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.title} ({self.get_status_display()})"

# =========================================================
# 06. PRODUCT MODEL
# =========================================================
class Product(ImageTagMixin):
    category: models.ForeignKey = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    brand: models.ForeignKey = models.ForeignKey(Brand, related_name='products', on_delete=models.CASCADE)
    title: models.CharField = models.CharField(max_length=150, unique=True)
    slug: models.SlugField = models.SlugField(max_length=150, unique=True, blank=True)
    old_price: models.DecimalField = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1000.00'))
    sale_price: models.DecimalField = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1000.00'))
    available_stock: models.PositiveIntegerField = models.PositiveIntegerField(validators=[MaxValueValidator(1000)], default=0)
    discount_percent: models.PositiveIntegerField = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], default=0)
    keyword: models.TextField = models.TextField(default='N/A')
    description: models.TextField = models.TextField(default='N/A')
    image: models.ImageField = models.ImageField(upload_to='products/%Y/%m/%d/', default='defaults/default.jpg')
    deadline: models.DateTimeField = models.DateTimeField(blank=True, null=True)
    is_deadline: models.BooleanField = models.BooleanField(default=False)
    is_featured: models.BooleanField = models.BooleanField(default=False)
    status: models.CharField = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')
    created_date: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_date: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '03. Products'

    def save(self, *args, **kwargs) -> None:
        # Discount discount sale_price active
        if self.discount_percent > 0:
            self.sale_price = (self.old_price * (Decimal(100) - Decimal(self.discount_percent)) / Decimal(100)).quantize(Decimal('0.01'))
        else:
            self.sale_price = self.old_price.quantize(Decimal('0.01'))

        self.full_clean()
        if not self.slug:
            self.slug = generate_unique_slug(Product, self.title)
        super().save(*args, **kwargs)

    def clean(self) -> None:
        # Sale price validation
        if self.sale_price > self.old_price:
            raise ValidationError("Sale price cannot be greater than old price.")
        # Deadline validation
        if self.deadline and self.deadline < timezone.now():
            raise ValidationError("Deadline cannot be in the past.")

    @property
    def remaining_seconds(self) -> int:
        if self.deadline and self.is_deadline:
            remaining = self.deadline - timezone.now()
            return max(0, int(remaining.total_seconds()))
        return 0

    @property
    def average_review(self) -> float:
        return float(self.reviews.filter(status='active').aggregate(Avg('rate'))['rate__avg'] or 0)

    @property
    def count_review(self) -> int:
        return self.reviews.filter(status='active').count()

    def __str__(self) -> str:
        return f"{self.title} ({self.get_status_display()})"

# =========================================================
# 07. IMAGE GALLERY MODEL
# =========================================================
class ImageGallery(ImageTagMixin):
    product: models.ForeignKey = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image: models.ImageField = models.ImageField(upload_to='images/%Y/%m/%d/', default='defaults/default.jpg')
    created_date: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_date: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '04. Image Galleries'

    def __str__(self) -> str:
        return f"{self.product.title} Image"

# =========================================================
# 08. COLOR MODEL
# =========================================================
class Color(ImageTagMixin):
    title: models.CharField = models.CharField(max_length=20, unique=True)
    code: models.CharField = models.CharField(max_length=20, unique=True)
    image: models.ImageField = models.ImageField(upload_to='colors/%Y/%m/%d/', default='defaults/default.jpg')
    created_date: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_date: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '05. Product Colors'

    def __str__(self) -> str:
        return f"{self.title} ({self.code})"

    @property
    def color_tag(self) -> str:
        if self.code:
            return mark_safe(f'<div style="width:30px; height:30px; background-color:{self.code}; border:1px solid #000;"></div>')
        return ""

# =========================================================
# 09. SIZE MODEL
# =========================================================
class Size(models.Model):
    title: models.CharField = models.CharField(max_length=20, unique=True)
    code: models.CharField = models.CharField(max_length=10, unique=True)
    created_date: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_date: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '06. Product Sizes'

    def __str__(self) -> str:
        return f"{self.title} ({self.code})"

# =========================================================
# 10. PRODUCT VARIANT MODEL
# =========================================================
class ProductVariant(ImageTagMixin):
    product: models.ForeignKey = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    color: models.ForeignKey = models.ForeignKey(Color, blank=True, null=True, on_delete=models.SET_NULL)
    size: models.ForeignKey = models.ForeignKey(Size, blank=True, null=True, on_delete=models.SET_NULL)
    variant_price: models.DecimalField = models.DecimalField(max_digits=10, decimal_places=2)
    available_stock: models.PositiveIntegerField = models.PositiveIntegerField(default=0)
    status: models.CharField = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')
    created_date: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_date: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'color', 'size')
        verbose_name_plural = '07. Product Variants'

    def __str__(self) -> str:
        return f"{self.product.title} - {self.size or 'No Size'} - {self.color or 'No Color'}"

# =========================================================
# 11. SLIDER MODEL
# =========================================================
class Slider(ImageTagMixin):
    product: models.ForeignKey = models.ForeignKey(Product, on_delete=models.CASCADE)
    title: models.CharField = models.CharField(max_length=150, unique=True)
    image: models.ImageField = models.ImageField(upload_to='sliders/%Y/%m/%d/', default='defaults/default.jpg')
    status: models.CharField = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')
    created_date: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_date: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '08. Sliders'

    def __str__(self) -> str:
        return f"{self.title} ({self.get_status_display()})"

# =========================================================
# 12. REVIEW MODEL
# =========================================================
class Review(models.Model):
    product: models.ForeignKey = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user: models.ForeignKey = models.ForeignKey(User, on_delete=models.CASCADE)
    subject: models.CharField = models.CharField(max_length=50, blank=True, null=True)
    comment: models.TextField = models.TextField(blank=True, null=True)
    rate: models.IntegerField = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])
    status: models.CharField = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')
    created_date: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_date: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '09. Reviews'

    def __str__(self) -> str:
        return self.subject if self.subject else f"Review by {self.user.username}"

# =========================================================
# 13. ADVANCEMENT MODEL
# =========================================================
class Advancement(ImageTagMixin):
    advancement_type: models.CharField = models.CharField(max_length=20, choices=ADVANCEMENT_TYPE_CHOICES, default='banner')
    product: models.ForeignKey = models.ForeignKey(Product, related_name='advancements', on_delete=models.CASCADE)
    title: models.CharField = models.CharField(max_length=150, unique=True, blank=True, null=True)
    subtitle: models.CharField = models.CharField(max_length=150, blank=True, null=True)
    image: models.ImageField = models.ImageField(upload_to='advancements/%Y/%m/%d/', default='defaults/default.jpg')
    status: models.CharField = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')
    created_date: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_date: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '10. Advancements'

    def __str__(self) -> str:
        return f"{self.title} ({self.get_status_display()})"

# =========================================================
# 14. ACCEPTANCE PAYMENT MODEL
# =========================================================
class AcceptancePayment(ImageTagMixin):
    title: models.CharField = models.CharField(max_length=150, unique=True, blank=True, null=True)
    subtitle: models.CharField = models.CharField(max_length=150, blank=True, null=True)
    image: models.ImageField = models.ImageField(upload_to='acceptance_payments/%Y/%m/%d/', default='defaults/default.jpg')
    amount: models.DecimalField = models.DecimalField(max_digits=10, decimal_places=2)
    status: models.CharField = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')
    created_date: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_date: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '11. Acceptance Payments'

    def __str__(self) -> str:
        return f"{self.title} ({self.get_status_display()})"
