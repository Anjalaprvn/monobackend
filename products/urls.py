from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # HTML endpoints
    path('', views.product_list_html, name='product_list'),
    path('add/', views.product_add_html, name='product_add'),
    path('view/', views.product_detail_html, name='product_detail'),
    path('<uuid:pk>/edit/', views.product_edit_html, name='product_edit'),
    path('<uuid:pk>/delete/', views.delete_product, name='delete_product'),
    # Minimal API endpoints (one GET, one POST)
    path('api/products/', views.product_list, name='api_product_list'),
    path('api/products/create/', views.create_product, name='create_product'),
]