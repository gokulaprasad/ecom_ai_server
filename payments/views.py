from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
import random
import string
from .models import Payment
from orders.models import Order
from .serializers import PaymentSerializer, ProcessPaymentSerializer


class ProcessPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ProcessPaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        order_id = data['order_id']
        
        # Get order
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if payment already exists
        if hasattr(order, 'payment'):
            return Response(
                {'error': 'Payment already processed for this order'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if order is pending
        if order.status != 'pending':
            return Response(
                {'error': f'Cannot process payment for order with status: {order.status}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Simulate payment processing
        simulate_success = data.get('simulate_success', True)
        
        # Generate transaction ID
        transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
        
        # Get last 4 digits of card if provided
        card_last_four = ''
        if data.get('card_number') and len(data['card_number']) >= 4:
            card_last_four = data['card_number'][-4:]
        
        # Create payment record
        payment = Payment.objects.create(
            order=order,
            user=request.user,
            payment_method=data['payment_method'],
            amount=order.total,
            status='processing',
            transaction_id=transaction_id,
            card_last_four=card_last_four,
            gateway_response={
                'simulated': True,
                'timestamp': str(datetime.now()) if 'datetime' in globals() else 'N/A'
            }
        )
        
        # Simulate payment result
        if simulate_success:
            payment.status = 'completed'
            payment.save()
            
            # Update order payment status
            order.payment_status = 'paid'
            order.status = 'processing'
            order.save()
            
            return Response({
                'success': True,
                'message': 'Payment processed successfully',
                'payment': PaymentSerializer(payment).data,
                'transaction_id': transaction_id
            })
        else:
            payment.status = 'failed'
            payment.save()
            
            return Response({
                'success': False,
                'message': 'Payment failed. Please try again or use a different payment method.',
                'payment': PaymentSerializer(payment).data
            }, status=status.HTTP_400_BAD_REQUEST)


class PaymentDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, payment_id):
        try:
            payment = Payment.objects.get(id=payment_id, user=request.user)
            serializer = PaymentSerializer(payment)
            return Response(serializer.data)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)


class OrderPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, order_number):
        try:
            order = Order.objects.get(order_number=order_number, user=request.user)
            if hasattr(order, 'payment'):
                serializer = PaymentSerializer(order.payment)
                return Response(serializer.data)
            return Response({'error': 'No payment found for this order'}, status=status.HTTP_404_NOT_FOUND)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


class UserPaymentsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        payments = Payment.objects.filter(user=request.user)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)


# Add datetime import
from datetime import datetime
