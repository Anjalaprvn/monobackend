from django.db import models
from django.utils import timezone
import uuid


class Client(models.Model):
    """Model for managing clients"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='clients/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
   

    def __str__(self):
        return self.name