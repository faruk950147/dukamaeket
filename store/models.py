from django.db import models
from django.utils.text import slugify
from django.utils.html import mark_safe
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Avg

User = get_user_model()


# =========================================================
# 01. STATUS CHOICES
# =========================================================
STATUS_CHOICES = (
    ('active', 'Active'),
    ('inactive', 'Inactive'),
)


# =========================================================
# 02. HELPER FUNCTION
# =========================================================
def generate_unique_slug(model_class, title):
    base_slug = slugify(title)
    slug = base_slug
    counter = 1

    while model_class.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


# =========================================================
# 03. CATEGORY MODEL
# =========================================================
class Category(models.Model):
    parent = models.ForeignKey(
        'self',
        related_name='children',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    title = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True)
    keyword = models.CharField(max_length=150, default='N/A')
    description = models.CharField(max_length=150, default='N/A')
    image = models.ImageField(upload_to='categories/%Y/%m/%d/')
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '01. Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Category, self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

    @property
    def image_tag(self):
        if self.image and hasattr(self.image, 'url'):
            return mark_safe(
                f'<img src="{self.image.url}" alt="{self.title}" '
                f'style="max-width:100px; max-height:100px;"/>'
            )
        return mark_safe('<span>No Image Available</span>')


# =========================================================
# 04. BRAND MODEL
# =========================================================
class Brand(models.Model):
    title = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True)
    keyword = models.CharField(max_length=150, default='N/A')
    description = models.CharField(max_length=150, default='N/A')
    image = models.ImageField(upload_to='brands/%Y/%m/%d/')
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '02. Brands'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Brand, self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

    @property
    def image_tag(self):
        if self.image and hasattr(self.image, 'url'):
            return mark_safe(
                f'<img src="{self.image.url}" alt="{self.title}" '
                f'style="max-width:50px; max-height:50px;"/>'
            )
        return mark_safe('<span>No Image Available</span>')


# =========================================================
# 05. PRODUCT MODEL
# =========================================================
class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, related_name='products', on_delete=models.CASCADE)
    title = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True)

    old_price = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)

    available_stock = models.PositiveIntegerField(
        validators=[MaxValueValidator(1000)],
        default=0
    )
    discount_percent = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0
    )

    keyword = models.TextField(default='N/A')
    description = models.TextField(default='N/A')

    image = models.ImageField(upload_to='products/%Y/%m/%d/')
    deadline = models.DateTimeField(blank=True, null=True)

    is_timeline = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')

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

        if self.deadline and self.deadline < timezone.now():
            raise ValidationError("Deadline cannot be in the past.")

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

    @property
    def image_tag(self):
        if self.image and hasattr(self.image, 'url'):
            return mark_safe(
                f'<img src="{self.image.url}" alt="{self.title}" '
                f'style="max-width:50px; max-height:50px;"/>'
            )
        return mark_safe('<span>No Image Available</span>')

    @property
    def remaining(self):
        if self.deadline and self.is_timeline == 'active':
            remaining = self.deadline - timezone.now()
            return max(0, int(remaining.total_seconds()))
        return 0

    @property
    def average_review(self):
        return float(
            self.reviews.filter(status='active').aggregate(Avg('rate'))['rate__avg'] or 0
        )

    @property
    def count_review(self):
        return self.reviews.filter(status='active').count()
   
   
# =========================================================
# 06. IMAGE GALLERY MODEL
# =========================================================
class ImageGallery(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/%Y/%m/%d/')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '04. Images Galleries'

    def __str__(self):
        return f"{self.product.title} - {self.image_tag}"

    @property
    def image_tag(self):
        if self.image and hasattr(self.image, 'url'):
            return mark_safe(
                f'<img src="{self.image.url}" alt="{self.product.title}" '
                f'style="max-width:50px; max-height:50px;"/>'
            )
        return mark_safe('<span>No Image Available</span>')


# =========================================================
# 07. COLOR MODEL
# =========================================================
class Color(models.Model):
    title = models.CharField(max_length=20, unique=True)
    code = models.CharField(max_length=20, unique=True)
    image = models.ImageField(upload_to='colors/%Y/%m/%d/')
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
                f'<div style="width:30px; height:30px; background-color:{self.code}; '
                f'border:1px solid #000;"></div>'
            )
        return ""
    
    @property
    def image_tag(self):
        if self.image and hasattr(self.image, 'url'):
            return mark_safe(
                f'<img src="{self.image.url}" alt="{self.title}" '
                f'style="max-width:50px; max-height:50px;"/>'
            )
        return mark_safe('<span>No Image Available</span>')


# =========================================================
# 08. SIZE MODEL
# =========================================================
class Size(models.Model):
    title = models.CharField(max_length=20, unique=True)
    code = models.CharField(max_length=10, unique=True)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '06. Product Sizes'

    def __str__(self):
        return f"{self.title} ({self.code})"


# =========================================================
# 09. SLIDER MODEL
# =========================================================
class Slider(models.Model):
    title = models.CharField(max_length=150, unique=True)
    image = models.ImageField(upload_to='sliders/%Y/%m/%d/')
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '07. Sliders'

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

    @property
    def image_tag(self):
        if self.image and hasattr(self.image, 'url'):
            return mark_safe(
                f'<img src="{self.image.url}" alt="{self.title}" '
                f'style="max-width:100px; max-height:50px;"/>'
            )
        return mark_safe('<span>No Image Available</span>')


# =========================================================
# 10. REVIEW MODEL
# =========================================================
class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    subject = models.CharField(max_length=50, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    rate = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '08. Reviews'

    def __str__(self):
        return self.subject if self.subject else f"Review by {self.user.username} on {self.product.title}"


# =========================================================
# 11. PRODUCT VARIANT MODEL
# =========================================================
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, blank=True, null=True)
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'color', 'size')
        verbose_name_plural = '09. Product Variants'

    def __str__(self):
        return f"{self.product.title} - {self.size or 'No Size'} - {self.color or 'No Color'}"

    @property
    def image_tag(self):
        if self.product.image and hasattr(self.product.image, 'url'):
            return mark_safe(f'<img src="{self.product.image.url}" width="50" height="50"/>')
        return "No Image"

