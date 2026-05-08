from django.urls import path
from . import views

app_name = 'service_enquiry'

urlpatterns = [
    # HTML endpoints
    path('', views.enquiry_list_html, name='enquiry_list'),
    path('add/', views.enquiry_add_html, name='enquiry_add'),
    path('<uuid:pk>/', views.enquiry_detail_html, name='enquiry_detail'),
    path('<uuid:pk>/edit/', views.enquiry_edit_html, name='enquiry_edit'),
    path('<uuid:pk>/delete/', views.delete_enquiry, name='delete_enquiry'),
    # Minimal API endpoints (one GET, one POST)
    path('api/enquiries/', views.enquiry_list, name='enquiry_list_api'),
    path('api/enquiries/create/', views.create_enquiry, name='create_enquiry_api'),
]