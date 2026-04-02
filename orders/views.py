from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models import Order, OrderItem
from cart.models import Cart, CartItem
from users.models import Address
from .serializers import (
    OrderListSerializer, OrderDetailSerializer, 
    PlaceOrderSerializer, UpdateOrderStatusSerializer, OrderAdminSerializer
)


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin()


class OrderListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)


class OrderDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, order_number):
        try:
            order = Order.objects.get(order_number=order_number, user=request.user)
            serializer = OrderDetailSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


class PlaceOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PlaceOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Get user's cart
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)
            if not cart_items.exists():
                return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        except Cart.DoesNotExist:
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get addresses
        data = serializer.validated_data
        
        if data.get('use_existing_address') and data.get('address_id'):
            try:
                address = Address.objects.get(id=data['address_id'], user=request.user)
                shipping_address = {
                    'street': address.street,
                    'city': address.city,
                    'state': address.state,
                    'zip_code': address.zip_code,
                    'country': address.country,
                }
                billing_address = shipping_address.copy()
            except Address.DoesNotExist:
                return Response({'error': 'Address not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            shipping_address = data['shipping_address']
            billing_address = data['billing_address']
        
        # Calculate totals
        subtotal = cart.get_subtotal()
        shipping_cost = 0 if subtotal > 50 else 10  # Free shipping over $50
        tax = subtotal * 0.08  # 8% tax
        total = subtotal + shipping_cost + tax
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            billing_address=billing_address,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            tax=tax,
            total=total,
            notes=data.get('notes', '')
        )
        
        # Create order items and update stock
        for cart_item in cart_items:
            product = cart_item.product
            
            # Check stock again
            if cart_item.quantity > product.stock:
                order.delete()
                return Response(
                    {'error': f'Not enough stock for {product.name}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                product_price=product.price,
                quantity=cart_item.quantity
            )
            
            # Update product stock
            product.stock -= cart_item.quantity
            product.save()
        
        # Clear cart
        cart_items.delete()
        
        return Response({
            'message': 'Order placed successfully',
            'order': OrderDetailSerializer(order).data
        }, status=status.HTTP_201_CREATED)


class CancelOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, order_number):
        try:
            order = Order.objects.get(order_number=order_number, user=request.user)
            
            if order.status not in ['pending', 'processing']:
                return Response(
                    {'error': 'Cannot cancel order at this stage'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Restore stock
            for item in order.items.all():
                if item.product:
                    item.product.stock += item.quantity
                    item.product.save()
            
            order.status = 'cancelled'
            order.save()
            
            return Response({
                'message': 'Order cancelled successfully',
                'order': OrderDetailSerializer(order).data
            })
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


# Admin Views
class AdminOrderListView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        orders = Order.objects.all()
        
        # Filter by status
        status_filter = request.query_params.get('status', '')
        if status_filter:
            orders = orders.filter(status=status_filter)
        
        # Filter by payment status
        payment_status = request.query_params.get('payment_status', '')
        if payment_status:
            orders = orders.filter(payment_status=payment_status)
        
        serializer = OrderAdminSerializer(orders, many=True)
        return Response(serializer.data)


class AdminOrderDetailView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request, order_number):
        try:
            order = Order.objects.get(order_number=order_number)
            serializer = OrderAdminSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


class UpdateOrderStatusView(APIView):
    permission_classes = [IsAdminUser]
    
    def put(self, request, order_number):
        serializer = UpdateOrderStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            order = Order.objects.get(order_number=order_number)
            new_status = serializer.validated_data['status']
            
            # Update timestamps based on status
            if new_status == 'shipped' and order.status != 'shipped':
                order.shipped_at = timezone.now()
                order.tracking_number = serializer.validated_data.get('tracking_number', '')
            elif new_status == 'delivered' and order.status != 'delivered':
                order.delivered_at = timezone.now()
            
            order.status = new_status
            order.save()
            
            return Response({
                'message': 'Order status updated',
                'order': OrderAdminSerializer(order).data
            })
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
