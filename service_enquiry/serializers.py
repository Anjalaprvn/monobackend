from rest_framework import serializers
from .models import ServiceEnquiry


class ServiceEnquirySerializer(serializers.ModelSerializer):
    """Serializer for ServiceEnquiry model"""
    
    class Meta:
        model = ServiceEnquiry
        fields = [
            'id', 'service', 'name', 'email', 'phone', 'message', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ServiceEnquiryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new service enquiries"""
    
    class Meta:
        model = ServiceEnquiry
        fields = [
            'service', 'name', 'email', 'phone', 'message'
        ]


# Response Serializers
class ServiceEnquiryListResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    count = serializers.IntegerField()
    enquiries = ServiceEnquirySerializer(many=True)


class ServiceEnquiryDetailResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    enquiry = ServiceEnquirySerializer()


class ServiceEnquiryCreateResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    enquiry = ServiceEnquirySerializer()


class APIResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField(required=False)
    error = serializers.CharField(required=False)