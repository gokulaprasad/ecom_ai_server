from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'is_active', 'product_count', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    discount_percentage = serializers.SerializerMethodField()
    primary_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price', 'compare_price', 'discount_percentage',
            'category', 'category_name', 'primary_image', 'rating', 'review_count',
            'is_active', 'is_featured', 'is_in_stock', 'created_at'
        ]
    
    def get_discount_percentage(self, obj):
        return obj.get_discount_percentage()
    
    def get_primary_image(self, obj):
        if obj.images and len(obj.images) > 0:
            return obj.images[0]
        return None
    
    def get_is_in_stock(self, obj):
        return obj.is_in_stock()


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    discount_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'compare_price',
            'discount_percentage', 'category', 'images', 'stock', 'sku',
            'rating', 'review_count', 'is_active', 'is_featured', 'tags',
            'specifications', 'created_at', 'updated_at'
        ]
    
    def get_discount_percentage(self, obj):
        return obj.get_discount_percentage()


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'description', 'price', 'compare_price',
            'category', 'images', 'stock', 'sku', 'is_active', 'is_featured',
            'tags', 'specifications'
        ]
    
    def validate_slug(self, value):
        if Product.objects.filter(slug=value).exists():
            if self.instance and self.instance.slug == value:
                return value
            raise serializers.ValidationError("Product with this slug already exists.")
        return value
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value
