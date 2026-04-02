from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Cart, CartItem
from products.models import Product
from .serializers import CartSerializer, CartItemSerializer, AddToCartSerializer, UpdateCartItemSerializer


class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_or_create_cart(self, user):
        cart, created = Cart.objects.get_or_create(user=user)
        return cart
    
    def get(self, request):
        cart = self.get_or_create_cart(request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class AddToCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data['product_id']
            quantity = serializer.validated_data['quantity']
            
            try:
                product = Product.objects.get(id=product_id, is_active=True)
            except Product.DoesNotExist:
                return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
            
            if quantity > product.stock:
                return Response(
                    {'error': f'Only {product.stock} items available in stock'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            cart, _ = Cart.objects.get_or_create(user=request.user)
            
            try:
                cart_item = CartItem.objects.get(cart=cart, product=product)
                new_quantity = cart_item.quantity + quantity
                if new_quantity > product.stock:
                    return Response(
                        {'error': f'Cannot add more. You already have {cart_item.quantity} in cart. Only {product.stock} available.'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                cart_item.quantity = new_quantity
                cart_item.save()
            except CartItem.DoesNotExist:
                cart_item = CartItem.objects.create(cart=cart, product=product, quantity=quantity)
            
            return Response({
                'message': 'Item added to cart',
                'cart_item': CartItemSerializer(cart_item).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateCartItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request, item_id):
        serializer = UpdateCartItemSerializer(data=request.data)
        if serializer.is_valid():
            quantity = serializer.validated_data['quantity']
            
            try:
                cart = Cart.objects.get(user=request.user)
                cart_item = CartItem.objects.get(id=item_id, cart=cart)
            except (Cart.DoesNotExist, CartItem.DoesNotExist):
                return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
            
            if quantity > cart_item.product.stock:
                return Response(
                    {'error': f'Only {cart_item.product.stock} items available in stock'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            cart_item.quantity = quantity
            cart_item.save()
            
            return Response({
                'message': 'Cart item updated',
                'cart_item': CartItemSerializer(cart_item).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RemoveCartItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, item_id):
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            cart_item.delete()
            return Response({'message': 'Item removed from cart'}, status=status.HTTP_204_NO_CONTENT)
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)


class ClearCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            cart.items.all().delete()
            return Response({'message': 'Cart cleared'}, status=status.HTTP_204_NO_CONTENT)
        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
