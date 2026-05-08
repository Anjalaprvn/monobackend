from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    # HTML endpoints
    path('', views.service_list_html, name='service_list'),
    path('add/', views.service_add_html, name='service_add'),
    path('<uuid:pk>/', views.service_detail_html, name='service_detail'),
    path('<uuid:pk>/edit/', views.service_edit_html, name='service_edit'),
    path('<uuid:pk>/delete/', views.delete_service, name='service_delete'),
    # Minimal API endpoints (one GET, one POST)
    path('api/services/', views.service_list, name='service_list_api'),
    path('api/services/create/', views.create_service, name='create_service_api'),
]