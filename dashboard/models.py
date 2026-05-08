from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
import uuid
import random
from datetime import datetime,timedelta
import os
from django.core.files.storage import FileSystemStorage


# Custom storage to save files within the dashboard app directory
testimonial_storage = FileSystemStorage(
    location=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'testimonials'),
    base_url='/dashboard/media/testimonials/'
)


def testimonial_image_upload_path(instance, filename):
    # This will upload images to dashboard/media/testimonials/ within the dashboard app directory
    return os.path.join('testimonials', filename)

class DashboardUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(username, email, password, **extra_fields)

class Dashboard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # This will store the hashed password
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_first_login = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    objects = DashboardUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.username
    
    def set_password(self, raw_password):
        from django.contrib.auth.hashers import make_password
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)

class OTPVerification(models.Model):
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    def is_expired(self):
        # OTP expires after 10 minutes
        expiration_time = self.created_at + timedelta(minutes=10)
        return datetime.now(expiration_time.tzinfo) > expiration_time
    
    def __str__(self):
        return f"{self.email} - {self.otp_code}"

class Role(models.Model):
    """Model for defining user roles and permissions"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    permissions = models.TextField(default='{}', blank=True)  # Store permissions as JSON string
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class UserRole(models.Model):
    """Model to assign roles to users"""
    user = models.ForeignKey(Dashboard, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('user', 'role')
    
    def __str__(self):
        return f"{self.user.username} - {self.role.name}"

class Testimonial(models.Model):
    """Model for managing testimonials"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    designation = models.CharField(max_length=150, blank=True)
    company = models.CharField(max_length=150, blank=True)
    message = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)  # 1-5 stars
    image = models.ImageField(upload_to=testimonial_image_upload_path, storage=testimonial_storage, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.name} - {self.company}"

class Enquiry(models.Model):
    """Model for managing enquiries"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    source = models.CharField(max_length=20, choices=[
        ('web', 'Web'),
        ('service', 'Service'),
        ('product', 'Product')
    ], blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.subject} - {self.name}"

class GlobalSetting(models.Model):
    """Model for storing global settings"""
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(Dashboard, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return self.key