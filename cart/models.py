from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from store.models import Product, ProductVariant
from decimal import Decimal

User = get_user_model()


# =========================================================
# 01. COUPON MODEL
# =========================================================
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
        verbose_name_plural = '01. Coupons'

    def clean(self):
        if self.expiry_date and self.expiry_date < timezone.now():
            raise ValidationError("Coupon has expired.")

    @property
    def is_valid(self) -> bool:
        """Check if coupon is active and not expired."""
        if not self.active:
            return False
        if self.expiry_date and self.expiry_date < timezone.now():
            return False
        return True

    def __str__(self):
        return f"{self.code} ({self.discount_type} - {self.discount_value})"


# =========================================================
# 02. CART MODEL
# =========================================================
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    paid = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '02. Carts'
        constraints = [
            models.UniqueConstraint(fields=['user', 'product', 'variant'], name='unique_cart_item')
        ]

    # ---- UNIT PRICE ----
    @property
    def unit_price(self) -> Decimal:
        if self.variant and self.variant.variant_price > Decimal('0.00'):
            return self.variant.variant_price
        return self.product.sale_price

    # ---- SUBTOTAL BEFORE DISCOUNT ----
    @property
    def subtotal(self) -> Decimal:
        return (self.unit_price * self.quantity).quantize(Decimal('0.01'))

    # ---- DISCOUNT AMOUNT ----
    @property
    def discount_amount(self) -> Decimal:
        if self.coupon and self.coupon.is_valid and self.subtotal >= self.coupon.min_purchase:
            if self.coupon.discount_type == 'percent':
                return (self.subtotal * self.coupon.discount_value / Decimal('100')).quantize(Decimal('0.01'))
            elif self.coupon.discount_type == 'fixed':
                return min(self.subtotal, self.coupon.discount_value)
        return Decimal('0.00')

    # ---- TOTAL AFTER DISCOUNT ----
    @property
    def total_price(self) -> Decimal:
        total = self.subtotal - self.discount_amount
        return total if total >= Decimal('0.00') else Decimal('0.00')

    # ---- STOCK VALIDATION ----
    def clean(self):
        """Ensure quantity does not exceed available stock."""
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

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        variant_str = f" - {self.variant}" if self.variant else ""
        return f"{self.user.username} - {self.product.title}{variant_str} ({self.quantity})"


# =========================================================
# 03. WISHLIST MODEL
# =========================================================
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '03. Wishlists'
        constraints = [
            models.UniqueConstraint(fields=['user', 'product', 'variant'], name='unique_wishlist_item')
        ]

    def __str__(self):
        variant_str = f" - {self.variant}" if self.variant else ""
        return f"{self.user.username} - {self.product.title}{variant_str}"
