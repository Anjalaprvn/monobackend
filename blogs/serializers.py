from rest_framework import serializers
from .models import Blog


class BlogSerializer(serializers.ModelSerializer):
    """Serializer for Blog model - used for list and detail views"""
    
    class Meta:
        model = Blog
        fields = [
            'id', 'title', 'slug', 'short_description', 'content',
            'cover_image', 'seo_title', 'seo_description', 'status',
            'published_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class BlogCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new blog posts"""
    slug = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Blog
        fields = [
            'title', 'slug', 'short_description', 'content',
            'cover_image', 'seo_title', 'seo_description', 'status'
        ]
    
    def validate_slug(self, value):
        """Ensure slug is unique"""
        if value and Blog.objects.filter(slug=value).exists():
            raise serializers.ValidationError("A blog with this slug already exists.")
        return value
    
    def create(self, validated_data):
        """Create blog post with auto-generated slug if not provided"""
        if not validated_data.get('slug'):
            from django.utils.text import slugify
            validated_data['slug'] = slugify(validated_data['title'])
        
        return super().create(validated_data)


class BlogListResponseSerializer(serializers.Serializer):
    """Response serializer for blog list API"""
    success = serializers.BooleanField()
    count = serializers.IntegerField()
    blogs = BlogSerializer(many=True)


class BlogDetailResponseSerializer(serializers.Serializer):
    """Response serializer for blog detail API"""
    success = serializers.BooleanField()
    blog = BlogSerializer()


class BlogCreateResponseSerializer(serializers.Serializer):
    """Response serializer for blog creation API"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    blog = BlogSerializer()


class APIResponseSerializer(serializers.Serializer):
    """Generic API response serializer"""
    success = serializers.BooleanField()
    message = serializers.CharField(required=False)
    error = serializers.CharField(required=False)