from django.db import models
from django.utils import timezone
import uuid
import os
from django.core.files.storage import FileSystemStorage


# Custom storage to save files within the gallery app directory
gallery_storage = FileSystemStorage(
    location=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'gallery', 'media', 'gallery'),
    base_url='/gallery/media/gallery/'
)


def gallery_image_upload_path(instance, filename):
    # This will upload images to gallery/media/gallery/ within the gallery app directory
    return os.path.join('gallery', filename)


class Gallery(models.Model):
    """Model for managing gallery items"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
   
    category = models.CharField(max_length=50, blank=True)
   
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
   

    def __str__(self):
        return self.title


class GalleryImage(models.Model):
    """Model for storing multiple images for a gallery item"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=gallery_image_upload_path, storage=gallery_storage)
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.gallery.title} - {self.image.name}"

    class Meta:
        ordering = ['created_at']