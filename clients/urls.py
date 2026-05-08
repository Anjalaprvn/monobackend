from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    # HTML endpoints
    path('', views.client_list_html, name='client_list'),
    path('add/', views.client_add_html, name='client_add'),
    path('view/<uuid:pk>/', views.client_detail_html, name='client_detail'),
    path('edit/<uuid:pk>/', views.client_edit_html, name='client_edit'),
    path('<uuid:pk>/delete/', views.delete_client, name='delete_client'),
    # Minimal API endpoints (one GET, one POST)
    path('api/clients/', views.client_list, name='api_client_list'),
    path('api/clients/create/', views.create_client, name='create_client'),
]