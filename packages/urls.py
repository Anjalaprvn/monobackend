from django.urls import path
from . import views

app_name = 'packages'

urlpatterns = [
    # HTML endpoints
    path('', views.package_list_html, name='package_list'),
    path('add/', views.package_add_html, name='package_add'),
    path('<uuid:pk>/', views.package_detail_html, name='package_detail'),
    path('<uuid:pk>/edit/', views.package_edit_html, name='package_edit'),
    path('<uuid:pk>/delete/', views.delete_package, name='delete_package'),
    # Minimal API endpoints (one GET, one POST)
    path('api/packages/', views.package_list, name='api_package_list'),
    path('api/packages/create/', views.create_package, name='create_package'),
]