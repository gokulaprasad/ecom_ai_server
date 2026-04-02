from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .models import Category, Product
from .serializers import (
    CategorySerializer, ProductListSerializer, 
    ProductDetailSerializer, ProductCreateUpdateSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin()


class CategoryListView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        categories = Category.objects.filter(is_active=True)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class CategoryDetailView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, slug):
        try:
            category = Category.objects.get(slug=slug, is_active=True)
            serializer = CategorySerializer(category)
            return Response(serializer.data)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)


class CategoryCreateUpdateDeleteView(APIView):
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, slug):
        try:
            category = Category.objects.get(slug=slug)
            serializer = CategorySerializer(category, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, slug):
        try:
            category = Category.objects.get(slug=slug)
            category.delete()
            return Response({'message': 'Category deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)


class ProductListView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        products = Product.objects.filter(is_active=True)
        
        # Search
        search = request.query_params.get('search', '')
        if search:
            products = products.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) |
                Q(tags__icontains=search)
            )
        
        # Category filter
        category = request.query_params.get('category', '')
        if category:
            products = products.filter(category__slug=category)
        
        # Price range filter
        min_price = request.query_params.get('min_price', '')
        max_price = request.query_params.get('max_price', '')
        if min_price:
            products = products.filter(price__gte=float(min_price))
        if max_price:
            products = products.filter(price__lte=float(max_price))
        
        # Rating filter
        min_rating = request.query_params.get('min_rating', '')
        if min_rating:
            products = products.filter(rating__gte=float(min_rating))
        
        # Featured filter
        featured = request.query_params.get('featured', '')
        if featured.lower() == 'true':
            products = products.filter(is_featured=True)
        
        # Sorting
        sort_by = request.query_params.get('sort', '-created_at')
        if sort_by == 'price_low':
            products = products.order_by('price')
        elif sort_by == 'price_high':
            products = products.order_by('-price')
        elif sort_by == 'rating':
            products = products.order_by('-rating')
        elif sort_by == 'name':
            products = products.order_by('name')
        else:
            products = products.order_by('-created_at')
        
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(products, request)
        serializer = ProductListSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class ProductDetailView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, slug):
        try:
            product = Product.objects.get(slug=slug, is_active=True)
            serializer = ProductDetailSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)


class ProductCreateUpdateDeleteView(APIView):
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        serializer = ProductCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, slug):
        try:
            product = Product.objects.get(slug=slug)
            serializer = ProductCreateUpdateSerializer(product, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, slug):
        try:
            product = Product.objects.get(slug=slug)
            product.delete()
            return Response({'message': 'Product deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)


class FeaturedProductsView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        products = Product.objects.filter(is_active=True, is_featured=True)[:8]
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


class RelatedProductsView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, slug):
        try:
            product = Product.objects.get(slug=slug)
            related = Product.objects.filter(
                category=product.category, 
                is_active=True
            ).exclude(id=product.id)[:4]
            serializer = ProductListSerializer(related, many=True)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
