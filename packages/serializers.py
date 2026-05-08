from rest_framework import serializers
from .models import Package


class PackageSerializer(serializers.ModelSerializer):
    """Serializer for Package model"""
    
    class Meta:
        model = Package
        fields = [
            'id', 'name', 'description', 'price', 'duration', 'features',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PackageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new packages"""
    
    class Meta:
        model = Package
        fields = [
            'name', 'description', 'price', 'duration', 'features',
            'is_active'
        ]


# Response Serializers
class PackageListResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    count = serializers.IntegerField()
    packages = PackageSerializer(many=True)


class PackageDetailResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    package = PackageSerializer()


class PackageCreateResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    package = PackageSerializer()


class APIResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField(required=False)
    error = serializers.CharField(required=False)