from django.db import models
import uuid
from django.utils import timezone
from django.utils.text import slugify
import os
from django.core.files.storage import FileSystemStorage


# Custom storage to save files within the blogs app directory
blog_storage = FileSystemStorage(
    location=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'blogs', 'media', 'blogs'),
    base_url='/blogs/media/blogs/'
)


def blog_image_upload_path(instance, filename):
    # This will upload images to blogs/media/blogs/ within the blogs app directory
    return os.path.join('blogs', filename)


class Blog(models.Model):
    """Blog model with complete fields"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    short_description = models.TextField(default='Short description')
    content = models.TextField(default='Content')  # Using TextField for simplicity, can be RichTextField
    cover_image = models.ImageField(upload_to=blog_image_upload_path, storage=blog_storage, blank=True, null=True)
    seo_title = models.CharField(max_length=200, blank=True)
    seo_description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        # Auto-set published_at when status changes to published
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
