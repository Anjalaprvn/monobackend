from django.urls import path
from . import views

app_name = 'gallery'

urlpatterns = [
    # HTML endpoints
    path('', views.gallery_list_html, name='gallery_list'),
    path('add/', views.gallery_add_html, name='gallery_add'),
    path('view/', views.gallery_latest_detail_html, name='gallery_latest_detail'),
    path('view/<uuid:pk>/', views.gallery_detail_html, name='gallery_detail'),
    path('<uuid:pk>/edit/', views.gallery_edit_html, name='gallery_edit'),
    path('<uuid:pk>/delete/', views.delete_gallery_item, name='delete_gallery_item'),
    # Minimal API endpoints (one GET, one POST)
    path('api/gallery/', views.gallery_list, name='api_gallery_list'),
    path('api/gallery/create/', views.create_gallery_item, name='create_gallery_item'),
]