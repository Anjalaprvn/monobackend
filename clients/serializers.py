from rest_framework import serializers
from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    """Serializer for Client model"""

    logo = serializers.ImageField(source='image', required=False)

    class Meta:
        model = Client
        fields = [
            'id',
            'name',
            'logo',      # API field
            'website',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

class ClientCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new clients"""
    
    # Accept 'logo' field from API (maps to 'image' field in model)
    logo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Client
        fields = [
            'id',
            'name',
            'website',
            'logo',      # API field name
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

# Response Serializers
class ClientListResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    count = serializers.IntegerField()
    clients = ClientSerializer(many=True)


class ClientDetailResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    client = ClientSerializer()


class ClientCreateResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    client = ClientSerializer()


class APIResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField(required=False)
    error = serializers.CharField(required=False)