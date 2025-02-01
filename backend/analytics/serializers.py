from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'amount', 'type', 'category', 'description', 'date']
        read_only_fields = ['id', 'user', 'date']
