from django.urls import path
from . import views

app_name = 'blogs'

urlpatterns = [
    # Minimal API endpoints (one GET, one POST)
    path('api/blogs/', views.blog_list, name='api_blog_list'),
    path('api/blogs/create/', views.create_blog, name='api_blog_create'),
    # HTML endpoints
    path('', views.blog_list, name='blog_list'),
    path('add/', views.blog_add, name='blog_add'),
    path('<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('edit/<uuid:blog_id>/', views.blog_edit, name='blog_edit'),
    
     path('delete/<int:blog_id>/', views.delete_blog, name='blog_delete'),

]