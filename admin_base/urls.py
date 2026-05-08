"""admin_base URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', include(('dashboard.urls', 'dashboard'), namespace='dashboard')),
    path('blogs/', include(('blogs.urls', 'blogs'), namespace='blogs')),
    path('services/', include(('services.urls', 'services'), namespace='services')),
    path('products/', include(('products.urls', 'products'), namespace='products')),
    path('gallery/', include(('gallery.urls', 'gallery'), namespace='gallery')),
    path('clients/', include(('clients.urls', 'clients'), namespace='clients')),
    path('packages/', include(('packages.urls', 'packages'), namespace='packages')),
    path('slots/', include(('slots.urls', 'slots'), namespace='slots')),
    path('booking/', include(('booking.urls', 'booking'), namespace='booking')),
    path('service_enquiry/', include(('service_enquiry.urls', 'service_enquiry'), namespace='service_enquiry')),
    path('admin/', admin.site.urls),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Also serve files from each app's media directory
    from django.views.static import serve
    import os
    
    def serve_dashboard_media(request, path):
        dashboard_media_root = os.path.join(settings.BASE_DIR, 'dashboard', 'media')
        return serve(request, path, document_root=dashboard_media_root)
    
    def serve_gallery_media(request, path):
        gallery_media_root = os.path.join(settings.BASE_DIR, 'gallery', 'media')
        return serve(request, path, document_root=gallery_media_root)
    
    def serve_products_media(request, path):
        products_media_root = os.path.join(settings.BASE_DIR, 'products', 'media')
        return serve(request, path, document_root=products_media_root)
    
    def serve_blogs_media(request, path):
        blogs_media_root = os.path.join(settings.BASE_DIR, 'blogs', 'media')
        return serve(request, path, document_root=blogs_media_root)
    
    def serve_services_media(request, path):
        services_media_root = os.path.join(settings.BASE_DIR, 'services', 'media')
        return serve(request, path, document_root=services_media_root)
    
    # Add URL patterns for each app's media files
    from django.urls import re_path
    urlpatterns += [
        re_path(r'^dashboard/media/(?P<path>.*)$', serve_dashboard_media, name='dashboard_media'),
        re_path(r'^gallery/media/(?P<path>.*)$', serve_gallery_media, name='gallery_media'),
        re_path(r'^products/media/(?P<path>.*)$', serve_products_media, name='products_media'),
        re_path(r'^blogs/media/(?P<path>.*)$', serve_blogs_media, name='blogs_media'),
        re_path(r'^services/media/(?P<path>.*)$', serve_services_media, name='services_media'),
    ]