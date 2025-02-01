from rest_framework import generics, permissions
from .models import Transaction
from .serializers import TransactionSerializer
from rest_framework.response import Response
from django.db.models import Sum
from datetime import datetime

class TransactionListCreateView(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

class InsightsView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        month = request.query_params.get("month")  # Format: YYYY-MM
        
        if not month:
            return Response({"error": "Month parameter is required (YYYY-MM)"}, status=400)

        try:
            start_date = datetime.strptime(month, "%Y-%m").replace(day=1)
            end_date = datetime.strptime(month, "%Y-%m").replace(day=28)  # Covers the whole month
        except ValueError:
            return Response({"error": "Invalid month format. Use YYYY-MM."}, status=400)

        transactions = Transaction.objects.filter(user=user, date__range=[start_date, end_date])

        total_expenses = transactions.filter(type="expense").aggregate(Sum("amount"))['amount__sum'] or 0
        total_revenue = transactions.filter(type="revenue").aggregate(Sum("amount"))['amount__sum'] or 0
        
        category_breakdown = (
            transactions
            .filter(type="expense")
            .values("category")
            .annotate(total=Sum("amount"))
            .order_by("-total")
        )
        
        top_category = category_breakdown[0]["category"] if category_breakdown else "None"

        return Response({
            "total_expenses": total_expenses,
            "total_revenue": total_revenue,
            "top_expense_category": top_category,
            "category_breakdown": {item["category"]: item["total"] for item in category_breakdown}
        })