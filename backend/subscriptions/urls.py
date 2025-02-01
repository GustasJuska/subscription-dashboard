from django.urls import path
from .views import CreateSubscriptionView

urlpatterns = [
    path("subscribe/", CreateSubscriptionView.as_view(), name="subscribe"),
]
