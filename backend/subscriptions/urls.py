from django.urls import path
from .views import CreateSubscriptionView, ListUserSubscriptionsView, CancelSubscriptionView, UpgradeSubscriptionView

urlpatterns = [
    path("subscribe/", CreateSubscriptionView.as_view(), name="subscribe"),
    path("subscriptions/", ListUserSubscriptionsView.as_view(), name="list-subscriptions"),
    path("cancel/", CancelSubscriptionView.as_view(), name="cancel-subscription"),
    path("upgrade/", UpgradeSubscriptionView.as_view(), name="upgrade-subscription"),
]
