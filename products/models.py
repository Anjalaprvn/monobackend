from django.db import models
from django.utils import timezone
import uuid
import os
from django.core.files.storage import FileSystemStorage


# Custom storage to save files within the products app directory
product_storage = FileSystemStorage(
    location=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'products', 'media', 'products'),
    base_url='/products/media/products/'
)


def product_image_upload_path(instance, filename):
    # This will upload images to products/media/products/ within the products app directory
    return os.path.join('products', filename)


class Product(models.Model):
    """Model for managing products"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100, blank=True)
    sku = models.CharField(max_length=50, unique=True, blank=True)  # Stock Keeping Unit
    stock_quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to=product_image_upload_path, storage=product_storage, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name