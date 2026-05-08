from rest_framework import serializers
from .models import Dashboard, Role, UserRole, Testimonial, Enquiry, GlobalSetting
import uuid
from django.contrib.auth.hashers import make_password


class DashboardSerializer(serializers.ModelSerializer):
    """Main serializer for Dashboard user model"""
    
    class Meta:
        model = Dashboard
        fields = [
            'id', 'username', 'email', 'is_staff', 
            'is_superuser', 'is_active', 'is_first_login', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def create(self, validated_data):
        # Hash the password before saving
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Hash the password if it's being updated
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)


class DashboardCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new Dashboard users"""
    
    class Meta:
        model = Dashboard
        fields = [
            'username', 'email', 'password', 'is_staff', 'is_superuser',
            'is_active', 'is_first_login'
        ]
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Dashboard(**validated_data)
        user.set_password(password)
        user.save()
        return user


class TestimonialSerializer(serializers.ModelSerializer):
    """Serializer for Testimonial model"""
    
    class Meta:
        model = Testimonial
        fields = [
            'id', 'name', 'designation', 'company', 'message', 
            'rating', 'image', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class TestimonialCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Testimonial model"""
    
    class Meta:
        model = Testimonial
        fields = [
            'name', 'designation', 'company', 'message', 
            'rating', 'image', 'is_active'
        ]
        
    def validate_rating(self, value):
        if value and (value < 1 or value > 5):
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value


class EnquirySerializer(serializers.ModelSerializer):
    """Serializer for Enquiry model"""
    
    class Meta:
        model = Enquiry
        fields = [
            'id', 'name', 'email', 'phone', 'subject', 'message',
            'source', 'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class EnquiryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new enquiries"""
    
    class Meta:
        model = Enquiry
        fields = [
            'name', 'email', 'phone', 'subject', 'message', 'source'
        ]


class GlobalSettingSerializer(serializers.ModelSerializer):
    """Serializer for GlobalSetting model"""
    updated_by_username = serializers.CharField(source='updated_by.username', read_only=True)
    
    class Meta:
        model = GlobalSetting
        fields = [
            'id', 'key', 'value', 'description', 
            'updated_at', 'updated_by', 'updated_by_username'
        ]
        read_only_fields = ['id', 'updated_at']


class GlobalSettingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new global settings"""
    
    class Meta:
        model = GlobalSetting
        fields = [
            'key', 'value', 'description'
        ]


# Response Serializers
class DashboardListResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    count = serializers.IntegerField()
    users = DashboardSerializer(many=True)


class DashboardDetailResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    user = DashboardSerializer()


class DashboardCreateResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    user = DashboardSerializer()


class TestimonialListResponseSerializer(serializers.Serializer):
    """Serializer for Testimonial list API response"""
    success = serializers.BooleanField()
    testimonials = TestimonialSerializer(many=True)
    count = serializers.IntegerField()


class TestimonialCreateResponseSerializer(serializers.Serializer):
    """Serializer for Testimonial create API response"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    testimonial = TestimonialSerializer()


class EnquiryListResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    count = serializers.IntegerField()
    enquiries = EnquirySerializer(many=True)


class EnquiryCreateResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    enquiry = EnquirySerializer()


class GlobalSettingListResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    count = serializers.IntegerField()
    settings = GlobalSettingSerializer(many=True)


class GlobalSettingCreateResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    setting = GlobalSettingSerializer()


class APIResponseSerializer(serializers.Serializer):
    """Generic API response serializer"""
    success = serializers.BooleanField()
    message = serializers.CharField(required=False)
    error = serializers.CharField(required=False)