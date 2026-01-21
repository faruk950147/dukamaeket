from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from store.models import Product, ProductVariant
from decimal import Decimal, ROUND_HALF_UP

User = get_user_model()


# ------------------------------
# Coupon Model
# ------------------------------
class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ('percent', 'Percent'),
        ('fixed', 'Fixed'),
    )

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    expiry_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = 'Coupons'

    def clean(self):
        if self.expiry_date and self.expiry_date < timezone.now():
            raise ValidationError("Coupon has expired.")

    @property
    def is_valid(self) -> bool:
        if not self.active:
            return False
        if self.expiry_date and self.expiry_date < timezone.now():
            return False
        return True

    def __str__(self):
        return f"{self.code} ({self.discount_type} - {self.discount_value})"


# ------------------------------
# Cart Model
# ------------------------------
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)

    # Stored price for production-safe checkout
    stored_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    paid = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = 'Carts'

    # Dynamic latest price (display only)
    @property
    def unit_price(self) -> Decimal:
        if self.variant and self.variant.variant_price > Decimal('0.00'):
            return self.variant.variant_price
        return self.product.sale_price

    # Subtotal using stored_unit_price
    @property
    def subtotal(self) -> Decimal:
        return (self.stored_unit_price * self.quantity).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    # Discount amount
    @property
    def discount_amount(self) -> Decimal:
        if self.coupon and self.coupon.is_valid and self.subtotal >= self.coupon.min_purchase:
            if self.coupon.discount_type == 'percent':
                return (self.subtotal * self.coupon.discount_value / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            elif self.coupon.discount_type == 'fixed':
                return min(self.subtotal, self.coupon.discount_value)
        return Decimal('0.00')

    # Total after discount
    @property
    def total_price(self) -> Decimal:
        total = self.subtotal - self.discount_amount
        return total if total >= Decimal('0.00') else Decimal('0.00')

    # Stock validation
    def clean(self):
        if self.variant:
            if self.quantity > self.variant.available_stock:
                raise ValidationError(
                    f"Only {self.variant.available_stock} unit(s) available for this variant."
                )
        else:
            if self.quantity > self.product.available_stock:
                raise ValidationError(
                    f"Cannot add more than {self.product.available_stock} unit(s) of {self.product.title}."
                )

    # Save method
    def save(self, *args, **kwargs):
        # Set stored_unit_price only when creating new item
        if not self.pk:
            self.stored_unit_price = self.unit_price
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        variant_str = f" - {self.variant}" if self.variant else ""
        return f"{self.user.username} - {self.product.title}{variant_str} ({self.quantity})"


# ------------------------------
# Wishlist Model
# ------------------------------
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = 'Wishlists'


    def __str__(self):
        variant_str = f" - {self.variant}" if self.variant else ""
        return f"{self.user.username} - {self.product.title}{variant_str}"
