from django.urls import path
from .views import TransactionListCreateView, TransactionDetailView, InsightsView

urlpatterns = [
    path('transactions/', TransactionListCreateView.as_view(), name='transaction-list-create'),
    path('transactions/<int:pk>/', TransactionDetailView.as_view(), name='transaction-detail'),
    path('insights/', InsightsView.as_view(), name='insights'),
]