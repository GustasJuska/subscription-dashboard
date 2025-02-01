from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True) # Users log in using emails (custome field) instead of username
    is_subscribed = models.BooleanField(default=False) # tracks whether a user has an active active subscription
    
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_groups",
        blank=True
    )

    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_permissions",
        blank=True
    )

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
        ("manager", "Manager")
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]