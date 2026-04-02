from rest_framework import serializers
from .models import Order, OrderItem
from products.models import Product


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'subtotal']
    
    def get_subtotal(self, obj):
        return obj.get_subtotal()


class OrderListSerializer(serializers.ModelSerializer):
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'payment_status', 
            'total', 'items_count', 'created_at'
        ]
    
    def get_items_count(self, obj):
        return obj.get_items_count()


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'payment_status',
            'shipping_address', 'billing_address', 'subtotal',
            'shipping_cost', 'tax', 'total', 'notes',
            'tracking_number', 'shipped_at', 'delivered_at',
            'items', 'items_count', 'created_at', 'updated_at'
        ]
    
    def get_items_count(self, obj):
        return obj.get_items_count()


class PlaceOrderSerializer(serializers.Serializer):
    shipping_address = serializers.DictField(required=True)
    billing_address = serializers.DictField(required=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    use_existing_address = serializers.BooleanField(default=False)
    address_id = serializers.CharField(required=False, allow_blank=True)
    
    def validate_shipping_address(self, value):
        required_fields = ['street', 'city', 'state', 'zip_code', 'country']
        for field in required_fields:
            if field not in value or not value[field]:
                raise serializers.ValidationError(f"{field} is required in shipping address.")
        return value


class UpdateOrderStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
    tracking_number = serializers.CharField(required=False, allow_blank=True)


class OrderAdminSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'user_email', 'status', 'payment_status',
            'shipping_address', 'billing_address', 'subtotal', 'shipping_cost',
            'tax', 'total', 'notes', 'tracking_number', 'shipped_at',
            'delivered_at', 'items', 'created_at', 'updated_at'
        ]
