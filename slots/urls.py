from django.urls import path
from . import views

app_name = 'slots'

urlpatterns = [
    path('', views.slot_list_html, name='slot_list'),
    path('add/', views.slot_add_html, name='slot_add'),
    path('<uuid:pk>/', views.slot_detail_html, name='slot_detail'),
    path('<uuid:pk>/edit/', views.slot_edit_html, name='slot_edit'),
    path('<uuid:pk>/delete/', views.delete_slot, name='delete_slot'),
    path('<uuid:pk>/book/', views.book_slot_html, name='book_slot'),
    path('<uuid:pk>/unbook/', views.unbook_slot, name='unbook_slot'),
    # API endpoints
    path('api/slots/', views.slot_list_api, name='slot_list_api'),  # GET endpoint
    path('api/slots/create/', views.create_slot_api, name='create_slot_api'),  # POST endpoint
    path('api/slots/<uuid:pk>/', views.update_slot_api, name='update_slot_api'),
    path('api/slots/<uuid:pk>/book/', views.book_slot_api, name='book_slot_api'),
]