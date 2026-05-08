from django.db import models
from django.utils import timezone
import uuid
import os
from django.core.files.storage import FileSystemStorage


# =========================
# Custom storage for service icons
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

service_icon_storage = FileSystemStorage(
    location=os.path.join(BASE_DIR, 'services', 'media', 'icons'),
    base_url='/services/media/icons/'
)


def service_icon_upload_path(instance, filename):
    """
    Upload icons directly into:
    services/media/icons/
    """
    return filename


class Service(models.Model):
    """Model for managing services"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100, blank=True, null=True)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to=service_icon_upload_path, storage=service_icon_storage, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Services"
        ordering = ['-created_at']