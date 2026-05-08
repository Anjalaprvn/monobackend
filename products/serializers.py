from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model"""
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'category', 'sku', 'stock_quantity',
            'image', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new products"""
    
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'price', 'category', 'sku', 'stock_quantity',
            'image', 'is_active'
        ]


# Response Serializers
class ProductListResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    count = serializers.IntegerField()
    products = ProductSerializer(many=True)


class ProductDetailResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    product = ProductSerializer()


class ProductCreateResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    product = ProductSerializer()


class APIResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField(required=False)
    error = serializers.CharField(required=False)