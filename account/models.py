from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.html import mark_safe
from django.dispatch import receiver
from django.db.models.signals import post_save


# ---------------- USER MANAGER ----------------
class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError("Username must be set")
        if not email:
            raise ValueError("Email must be set")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)


# ---------------- USER ----------------
class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[UnicodeUsernameValidator()],
        blank=False,
        null=False
    )
    email = models.EmailField(
        max_length=150,
        unique=True,
        blank=False,
        null=False
    )
    image = models.ImageField(upload_to='user', default='defaults/default.jpg')
    country = models.CharField(max_length=150, null=True, blank=True)
    city = models.CharField(max_length=150, null=True, blank=True)
    home_city = models.CharField(max_length=150, null=True, blank=True)
    zip_code = models.CharField(max_length=15, null=True, blank=True)
    phone = models.CharField(max_length=16, null=True, blank=True)
    address = models.TextField(max_length=500, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        ordering = ['id']
        verbose_name_plural = '01. Users'
        
    @property
    def image_tag(self):
        if self.image:
            return mark_safe(f'<img src="{self.image.url}" width="50" height="50"/>')
        return mark_safe('<span>No Image</span>')

    def __str__(self):
        return self.username


# ---------------- Shipping ----------------
class Shipping(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipping')
    country = models.CharField(max_length=150, null=True, blank=True)
    city = models.CharField(max_length=150, null=True, blank=True)
    home_city = models.CharField(max_length=150, null=True, blank=True)
    zip_code = models.CharField(max_length=15, null=True, blank=True)
    phone = models.CharField(max_length=16, null=True, blank=True)
    address = models.TextField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '02. Shipping'

    def __str__(self):
        return f"{self.user.username}'s Shipping"


# ---------------- SIGNAL ----------------
@receiver(post_save, sender=User)
def create_or_update_shipping_address(sender, instance, created, **kwargs):
    if created:
        Shipping.objects.create(user=instance)
    else:
        if hasattr(instance, 'shipping'):
            instance.shipping.save()
