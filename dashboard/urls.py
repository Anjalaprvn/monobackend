from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.base, name="base"),
    path("index/", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("reset-password/", views.reset_password, name="reset_password"),
    
    # Forgot password functionality
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("forgot-password/verify-otp/", views.forgot_password_verify_otp, name="forgot_password_verify_otp"),
    path("forgot-password/reset/", views.forgot_password_reset, name="forgot_password_reset"),
    path("forgot-password/resend-otp/", views.resend_forgot_password_otp, name="resend_forgot_password_otp"),
    path("logout/", views.logout_view, name="logout"),
    path("home/", views.dashboard_home, name="home"),
    path("profile/", views.user_profile, name="profile"),
    path("users/", views.user_list, name="user_list"),
    path("users/<uuid:user_id>/", views.user_detail, name="user_detail"),
    
    # Minimal API endpoints for dashboard users
    path("api/users/", views.api_dashboard_list, name="api_users_list"),
    path("api/users/create/", views.api_dashboard_create, name="api_user_create"),
    
    path("enquiry/", views.enquiry_list, name="enquiry_list"),
    path("blog/", views.blog_list, name="blog_list"),
    path("blog/add/", views.blog_add, name="blog_add"),
    path("blog/view/", views.blog_view, name="blog_view"),
    path("payment/", views.payment_history, name="payment_history"),
    path("token/", views.token_management, name="token_management"),
    path("api/token/auth/", views.get_jwt_token, name="api_token_auth"),
    path("api/token/refresh/", views.refresh_jwt_token, name="api_token_refresh"),
    path("leads/", views.lead_management, name="lead_management"),
    path("matching/", views.matching_engine, name="matching_engine"),
  
    # New functionality URLs 
    path("testimonial-management/", views.testimonial_management, name="testimonial_management"),
    path("add-testimonial/", views.add_testimonial, name="add_testimonial"),
    path("testimonials/", views.testimonial_list, name="testimonial_list"),
    path("testimonials/<uuid:pk>/", views.view_testimonial, name="view_testimonial"),
    path("testimonials/<uuid:pk>/edit/", views.edit_testimonial, name="edit_testimonial"),
    path("testimonials/<uuid:pk>/delete/", views.delete_testimonial, name="delete_testimonial"),
    path("enquiry-management/", views.enquiry_management, name="enquiry_management"),
    path("client-logo/", views.client_logo_management, name="client_logo_management"),
    path("client-logo/view/<uuid:client_id>/", views.client_logo_management, name="client_logo_view"),
    path("client-logo/edit/<uuid:client_id>/", views.client_logo_management, name="client_logo_edit"),
    path("global-settings/", views.global_settings, name="global_settings"),
    path("dashboard-settings/", views.dashboard_settings, name="dashboard_settings"),
    
    # Minimal API endpoints for testimonials
    path("api/testimonials/", views.api_testimonials_list, name="api_testimonials_list"),
    path("api/testimonials/create/", views.api_testimonial_create, name="api_testimonials_create"),
    
    # Minimal API endpoints for enquiries
    path("api/enquiries/", views.api_enquiries_list, name="api_enquiries_list"),
    path("api/enquiries/create/", views.api_enquiry_create, name="api_enquiries_create"),
]