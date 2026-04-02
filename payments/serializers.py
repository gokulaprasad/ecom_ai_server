from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'order_number', 'payment_method', 'amount',
            'status', 'transaction_id', 'card_last_four', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'transaction_id', 'created_at']


class ProcessPaymentSerializer(serializers.Serializer):
    order_id = serializers.CharField(required=True)
    payment_method = serializers.ChoiceField(choices=Payment.PAYMENT_METHOD_CHOICES, default='credit_card')
    
    # Card details (for mock purposes)
    card_number = serializers.CharField(required=False, allow_blank=True)
    card_expiry = serializers.CharField(required=False, allow_blank=True)
    card_cvv = serializers.CharField(required=False, allow_blank=True)
    card_name = serializers.CharField(required=False, allow_blank=True)
    
    # Simulate success/failure
    simulate_success = serializers.BooleanField(default=True)
    
    def validate_card_number(self, value):
        if value and len(value) >= 4:
            return value
        return value


class PaymentResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    payment = PaymentSerializer(required=False)
    transaction_id = serializers.CharField(required=False)
