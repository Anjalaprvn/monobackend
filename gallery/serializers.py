from rest_framework import serializers
from .models import Gallery, GalleryImage


class GalleryImageSerializer(serializers.ModelSerializer):
    """Serializer for GalleryImage model"""
    
    class Meta:
        model = GalleryImage
        fields = ['id', 'image', 'caption', 'is_primary', 'created_at']
        read_only_fields = ['id', 'created_at']


class GallerySerializer(serializers.ModelSerializer):
    """Serializer for Gallery model with images"""
    images = GalleryImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Gallery
        fields = [
            'id', 'title', 'category', 'is_active', 'created_at', 'images'
        ]
        read_only_fields = ['id', 'created_at']


class GalleryCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Gallery
        fields = ['title', 'category', 'is_active', 'images']

    def create(self, validated_data):
       
        images = validated_data.pop('images', [])

       
        gallery = Gallery.objects.create(**validated_data)

       
        for index, image in enumerate(images):
            GalleryImage.objects.create(
                gallery=gallery,
                image=image,
                is_primary=(index == 0)
            )

        return gallery


# Response Serializers
class GalleryListResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    count = serializers.IntegerField()
    galleries = GallerySerializer(many=True)


class GalleryDetailResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    gallery = GallerySerializer()


class GalleryCreateResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    gallery = GallerySerializer()


class APIResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField(required=False)
    error = serializers.CharField(required=False)