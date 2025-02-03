from django.db import models
from django.conf import settings

class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=255)
    stripe_subscription_id = models.CharField(max_length=255)
    plan = models.CharField(max_length=50, default="basic")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    PLAN_CHOICES = [
    ("basic", "Basic"),
    ("pro", "Pro"),
    ("enterprise", "Enterprise"),
    ]

    plan = models.CharField(max_length=50, choices=PLAN_CHOICES, default="basic")


    def __str__(self):
        return f"Subscription of {self.user.email} for plan {self.plan}"
