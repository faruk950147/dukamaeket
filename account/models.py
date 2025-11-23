from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.html import mark_safe
from django.dispatch import receiver
from django.db.models.signals import post_save

# Custom user manager
from account.managers import UserManager


# ---------------- USER ----------------
class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[UnicodeUsernameValidator()],
    )
    email = models.EmailField(
        max_length=150,
        unique=True
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    joined_date = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        ordering = ['id']
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username


# ---------------- PROFILE ----------------
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    image = models.FileField(upload_to='profiles', null=True, blank=True)
    country = models.CharField(max_length=150, null=True, blank=True)
    city = models.CharField(max_length=150, null=True, blank=True)
    home_city = models.CharField(max_length=150, null=True, blank=True)
    zip_code = models.CharField(max_length=15, null=True, blank=True)
    phone = models.CharField(max_length=16, null=True, blank=True)
    address = models.TextField(max_length=500, null=True, blank=True)
    joined_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = 'Profiles'

    @property
    def image_tag(self):
        if self.image:
            return mark_safe(f'<img src="{self.image.url}" width="50" height="50"/>')
        return mark_safe('<span>No Image</span>')

    def __str__(self):
        return f"{self.user.username}'s Profile"


# ---------------- SIGNAL ----------------
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create a profile automatically when a new user is created
        Profile.objects.create(user=instance)
    else:
        # Save profile when user is updated
        instance.profile.save()
