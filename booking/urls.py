from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    # HTML endpoints
    path('', views.booking_list_html, name='booking_list'),
    path('add/', views.booking_add_html, name='booking_add'),
    path('<uuid:pk>/', views.booking_detail_html, name='booking_detail'),
    path('<uuid:pk>/edit/', views.booking_edit_html, name='booking_edit'),
    path('<uuid:pk>/delete/', views.delete_booking_html, name='delete_booking'),
    path('slots/', views.slot_list_html, name='slot_list'),
    path('slots/add/', views.slot_add_html, name='slot_add'),
    path('slots/<uuid:pk>/', views.slot_detail_html, name='slot_detail'),
    path('slots/<uuid:pk>/edit/', views.slot_edit_html, name='slot_edit'),
    path('slots/<uuid:pk>/delete/', views.delete_slot, name='delete_slot'),
    path('slots/<uuid:pk>/book/', views.book_slot, name='book_slot'),
    # Minimal API endpoints (one GET, one POST)
    path('api/bookings/', views.booking_list, name='booking_list_api'),
    path('api/bookings/create/', views.create_booking, name='create_booking_api'),
]