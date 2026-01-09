from django.db import models
from django.contrib.auth import get_user_model
from account.models import Profile
from store.models import Product, ProductVariant

User = get_user_model()

STATUS_CHOICES = (
    ('Pending', 'Pending'),
    ('Accepted','Accepted'),
    ('Packed','Packed'),
    ('On the Way', 'On the Way'),
    ('Delivered','Delivered'),
    ('Canceled','Canceled'),
)

DELIVERY_METHODS = (
    ('COD', 'Cash On Delivery'),
    ('PayPal', 'PayPal'),
)

class Checkout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="checkouts")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    is_checkout = models.BooleanField(default=False)
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_METHODS, default='COD')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = '01. Checkout'

    def __str__(self):
        return f"Checkout #{self.id} by {self.user.username} - {self.status}"

    # Total quantity of items in this checkout
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    # Total price of checkout
    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

class CheckoutItem(models.Model):
    checkout = models.ForeignKey(Checkout, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="checkout_items", on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, null=True, blank=True, on_delete=models.SET_NULL, related_name="checkout_items")
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        if self.variant:
            return f"{self.product.title} ({self.variant}) x {self.quantity}"
        return f"{self.product.title} x {self.quantity}"

    # Calculate total price for this item
    def total_price(self):
        price = self.variant.variant_price if self.variant else self.product.sale_price
        return price * self.quantity

"""
class Checkout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, null=True, blank=True, on_delete=models.SET_NULL)

    quantity = models.PositiveIntegerField(default=1)
    check_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    is_ordered = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=50, choices=DELIVERY_METHODS, default='COD')

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_cost(self):
        return self.quantity * self.check_price

    def save(self, *args, **kwargs):
        if not self.check_price:
            self.check_price = self.variant.variant_price if self.variant else self.product.sale_price
        super().save(*args, **kwargs)

    def reduce_stock(self):
        # Reduce stock after order is placed.
        if self.variant:
            if self.variant.available_stock >= self.quantity:
                self.variant.available_stock -= self.quantity
                self.variant.save()
            else:
                raise ValueError("Not enough variant stock")
        else:
            if self.product.available_stock >= self.quantity:
                self.product.available_stock -= self.quantity
                self.product.save()
            else:
                raise ValueError("Not enough product stock")

    def mark_as_ordered(self):
        # Mark checkout as ordered and reduce stock
        if not self.is_ordered:
            self.reduce_stock()
            self.is_ordered = True
            self.status = 'Accepted'
            self.save()

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"



"""