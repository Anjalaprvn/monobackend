from django.db import models
from django.utils import timezone
import uuid


class Package(models.Model):
    """Model for managing packages"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=50, blank=True)  # e.g., "Monthly", "Yearly", "One-time"
    features = models.TextField(blank=True)  # JSON string or comma-separated features
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name