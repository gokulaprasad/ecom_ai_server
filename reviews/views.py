from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Avg, Count
from .models import Review, ReviewHelpful
from products.models import Product
from orders.models import Order, OrderItem
from .serializers import ReviewSerializer, CreateReviewSerializer, ReviewSummarySerializer


class ProductReviewsView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, product_slug):
        try:
            product = Product.objects.get(slug=product_slug)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
        reviews = Review.objects.filter(product=product)
        
        # Filter by rating
        rating = request.query_params.get('rating', '')
        if rating:
            reviews = reviews.filter(rating=int(rating))
        
        serializer = ReviewSerializer(reviews, many=True)
        
        # Calculate summary
        summary = {
            'average_rating': product.rating,
            'total_reviews': product.review_count,
            'rating_breakdown': self.get_rating_breakdown(product)
        }
        
        return Response({
            'reviews': serializer.data,
            'summary': summary
        })
    
    def get_rating_breakdown(self, product):
        breakdown = {}
        for i in range(1, 6):
            count = Review.objects.filter(product=product, rating=i).count()
            breakdown[str(i)] = count
        return breakdown


class CreateReviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, product_slug):
        try:
            product = Product.objects.get(slug=product_slug)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if user already reviewed this product
        if Review.objects.filter(user=request.user, product=product).exists():
            return Response(
                {'error': 'You have already reviewed this product'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CreateReviewSerializer(data=request.data)
        if serializer.is_valid():
            # Check if verified purchase
            is_verified = OrderItem.objects.filter(
                order__user=request.user,
                product=product,
                order__status='delivered'
            ).exists()
            
            review = serializer.save(
                user=request.user,
                product=product,
                is_verified_purchase=is_verified
            )
            
            return Response({
                'message': 'Review submitted successfully',
                'review': ReviewSerializer(review).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateReviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request, review_id):
        try:
            review = Review.objects.get(id=review_id, user=request.user)
        except Review.DoesNotExist:
            return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CreateReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Review updated successfully',
                'review': ReviewSerializer(review).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, review_id):
        try:
            review = Review.objects.get(id=review_id, user=request.user)
            review.delete()
            return Response({'message': 'Review deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Review.DoesNotExist:
            return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)


class MarkReviewHelpfulView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, review_id):
        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if user already marked as helpful
        if ReviewHelpful.objects.filter(review=review, user=request.user).exists():
            return Response(
                {'error': 'You already marked this review as helpful'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ReviewHelpful.objects.create(review=review, user=request.user)
        review.helpful_count += 1
        review.save()
        
        return Response({
            'message': 'Review marked as helpful',
            'helpful_count': review.helpful_count
        })


class UserReviewsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        reviews = Review.objects.filter(user=request.user)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
