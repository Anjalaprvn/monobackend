from rest_framework import serializers
from .models import Service


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for Service model"""
    
    class Meta:
        model = Service
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ServiceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new services"""
    
    class Meta:
        model = Service
        fields = [
            'name', 'slug', 'description', 'icon', 'is_active'
        ]


# Response Serializers
class ServiceListResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    count = serializers.IntegerField()
    services = ServiceSerializer(many=True)


class ServiceDetailResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    service = ServiceSerializer()


class ServiceCreateResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    service = ServiceSerializer()


class APIResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField(required=False)
    error = serializers.CharField(required=False)