from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from rest_framework import status
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils import timezone
from .models import Dashboard, OTPVerification, Role, UserRole, Testimonial, Enquiry, GlobalSetting
from .utils import send_otp_email, verify_otp_code
import random
from .serializers import (
    DashboardSerializer, DashboardCreateSerializer,
    TestimonialSerializer, TestimonialCreateSerializer,
    EnquirySerializer, EnquiryCreateSerializer,
    GlobalSettingSerializer, GlobalSettingCreateSerializer,
    DashboardListResponseSerializer, DashboardCreateResponseSerializer,
    TestimonialListResponseSerializer, TestimonialCreateResponseSerializer,
    EnquiryListResponseSerializer, EnquiryCreateResponseSerializer,
    GlobalSettingListResponseSerializer, GlobalSettingCreateResponseSerializer,
    APIResponseSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import json
from functools import wraps


def custom_login_required(view_func):
    """
    Custom login required decorator that preserves the next URL
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.session.get('is_authenticated'):
            return view_func(request, *args, **kwargs)
        else:
            # Store the requested URL to redirect back after login
            request.session['next_url'] = request.get_full_path()
            return redirect('dashboard:login')
    return _wrapped_view


def login_view(request):
    """
    Handle user login with OTP verification and improved error handling
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        # Debug information
        print(f"=== LOGIN ATTEMPT ===")
        print(f"Email provided: '{email}'")
        print(f"Password provided: {'Yes' if password else 'No'}")
        
        # Check if fields are provided
        if not email or not password:
            messages.error(request, 'Please enter both email and password')
            return render(request, 'login.html')
        
        try:
            # Count total users for debugging
            total_users = Dashboard.objects.count()
            print(f"Total users in database: {total_users}")
            
            if total_users == 0:
                messages.error(request, 'No users found in the system. Please contact administrator.')
                return render(request, 'login.html')
            
            # Try to find user by email (case-insensitive)
            try:
                user = Dashboard.objects.get(email__iexact=email)
                print(f"Found user: {user.username} (active: {user.is_active})")
                
                # Check if user is active
                if not user.is_active:
                    messages.error(request, 'Account is deactivated. Please contact administrator.')
                    return render(request, 'login.html')
                
                # Verify password
                if user.check_password(password):
                    print("Password verified successfully")
                    
                    # Generate and send OTP
                    try:
                        otp_record = send_otp_email(email)
                        print(f"OTP sent successfully: {otp_record.otp_code}")
                        
                        # Store user info in session
                        request.session['pending_user_id'] = str(user.id)
                        request.session['pending_email'] = email
                        
                        messages.success(request, 'OTP has been sent to your email')
                        return redirect('dashboard:verify_otp')
                    except Exception as e:
                        print(f"Error sending OTP: {e}")
                        messages.error(request, f'Failed to send verification code: {str(e)}. Please try again.')
                        return render(request, 'login.html')
                else:
                    print("Password verification failed")
                    messages.error(request, 'Invalid email or password')
            except Dashboard.DoesNotExist:
                print("User not found with that email")
                # Show all available emails for debugging
                all_emails = list(Dashboard.objects.values_list('email', flat=True))
                print(f"Available emails in database: {all_emails}")
                messages.error(request, 'Invalid email or password')
                
        except Exception as e:
            print(f"Unexpected error during login: {e}")
            messages.error(request, f'An error occurred: {str(e)}')
    
    return render(request, 'login.html')

def forgot_password(request):
    """
    Handle forgot password request - send OTP to user's email
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        if not email:
            messages.error(request, 'Please enter your email address')
            return render(request, 'forgot_password.html')
        
        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Please enter a valid email address')
            return render(request, 'forgot_password.html')
        
        # Check if user exists
        try:
            user = Dashboard.objects.get(email__iexact=email)
            
            # Generate and send OTP for password reset
            otp_record = send_otp_email(email)
            
            # Store email in session for verification
            request.session['forgot_password_email'] = email
            
            messages.success(request, 'OTP has been sent to your email for password reset')
            return redirect('dashboard:forgot_password_verify_otp')
            
        except Dashboard.DoesNotExist:
            messages.error(request, 'No account found with this email address')
            return render(request, 'forgot_password.html')
    
    return render(request, 'forgot_password.html')

def forgot_password_verify_otp(request):
    """
    Verify OTP sent for password reset
    """
    email = request.session.get('forgot_password_email')
    
    if not email:
        messages.error(request, 'Session expired. Please try again.')
        return redirect('dashboard:forgot_password')
    
    if request.method == 'POST':
        # Get OTP from form (separate input fields)
        otp_digits = []
        for i in range(1, 7):
            digit = request.POST.get(f'otp_digit_{i}')
            if digit:
                otp_digits.append(digit)
            else:
                break
        
        otp_code = ''.join(otp_digits)
        
        if len(otp_code) != 6:
            messages.error(request, 'Please enter a complete 6-digit OTP')
            return render(request, 'forgot_password_otp_verification.html', {'email': email})
        
        # Verify the OTP
        if verify_otp_code(email, otp_code):
            # OTP verified successfully, proceed to reset password
            messages.success(request, 'OTP verified successfully. Please reset your password.')
            return redirect('dashboard:forgot_password_reset')
        else:
            messages.error(request, 'Invalid or expired OTP. Please try again.')
    
    return render(request, 'forgot_password_otp_verification.html', {'email': email})

def forgot_password_reset(request):
    """
    Handle password reset after OTP verification
    """
    email = request.session.get('forgot_password_email')
    
    if not email:
        messages.error(request, 'Session expired. Please try again.')
        return redirect('dashboard:forgot_password')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validate passwords
        if not new_password or len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'forgot_password_reset.html', {'email': email})
        
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'forgot_password_reset.html', {'email': email})
        
        # Update password
        try:
            user = Dashboard.objects.get(email__iexact=email)
            user.set_password(new_password)
            user.save()
            
            # Clear the session
            if 'forgot_password_email' in request.session:
                del request.session['forgot_password_email']
            
            messages.success(request, 'Password has been reset successfully! Please login with your new password.')
            return redirect('dashboard:login')
            
        except Dashboard.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('dashboard:login')
    
    return render(request, 'forgot_password_reset.html', {'email': email})

def resend_forgot_password_otp(request):
    """
    Resend OTP for forgot password flow
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        if not email:
            return JsonResponse({
                'success': False,
                'error': 'Email is required'
            })
        
        try:
            # Validate email format
            validate_email(email)
            
            # Check if user exists
            user = Dashboard.objects.get(email__iexact=email)
            
            # Generate and send new OTP
            otp_record = send_otp_email(email)
            
            return JsonResponse({
                'success': True,
                'message': 'OTP has been resent to your email'
            })
            
        except ValidationError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid email address'
            })
        except Dashboard.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'No account found with this email address'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })

def verify_otp(request):
    """
    Verify the OTP sent to user's email
    """
    if request.method == 'POST':
        otp_code = request.POST.get('otp_code')
        email = request.session.get('pending_email')
        
        if not email:
            messages.error(request, 'Session expired. Please login again.')
            return redirect('dashboard:login')
        
        if verify_otp_code(email, otp_code):
            # OTP verified successfully, log the user in
            user_id = request.session.get('pending_user_id')
            user = Dashboard.objects.get(id=user_id)
            
            # Set session data to indicate user is logged in
            request.session['user_id'] = str(user.id)
            request.session['username'] = user.username
            request.session['is_authenticated'] = True
            
            # Clear pending session data
            if 'pending_user_id' in request.session:
                del request.session['pending_user_id']
            if 'pending_email' in request.session:
                del request.session['pending_email']
            
            # Check if there's a 'next' parameter in session to redirect to original page
            next_url = request.session.pop('next_url', None)
            
            # Check if it's first login
            if user.is_first_login:
                # Redirect to password reset page for first-time users
                return redirect('dashboard:reset_password')
            else:
                # Redirect to next_url if available, otherwise to dashboard index
                if next_url:
                    return redirect(next_url)
                else:
                    # Redirect to index page for returning users
                    return redirect('dashboard:index')
        else:
            messages.error(request, 'Invalid or expired OTP. Please try again.')
    
    return render(request, 'verify_otp.html')

def reset_password(request):
    """
    Handle password reset for first-time login
    """
    # Check if user is authenticated through session
    if not request.session.get('is_authenticated'):
        messages.error(request, 'Please login first.')
        return redirect('dashboard:login')
    
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Invalid session. Please login again.')
        return redirect('dashboard:login')
    
    try:
        user = Dashboard.objects.get(id=user_id)
    except Dashboard.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('dashboard:login')
    
    # Check if it's actually first login
    if not user.is_first_login:
        # If not first login, redirect to index with full dashboard
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validate passwords
        if not new_password or len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'first_login_reset.html', {'user_id': user_id})
        
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'first_login_reset.html', {'user_id': user_id})
        
        # Update password and mark first login as completed
        user.set_password(new_password)
        user.is_first_login = False
        user.save()
        
        messages.success(request, 'Password updated successfully! Welcome to the dashboard.')
        # After first login, show full dashboard with sidebar
        return redirect('dashboard:index')
    
    # For GET requests, show the standalone reset page
    return render(request, 'first_login_reset.html', {'user_id': user_id})

def logout_view(request):
    """
    Handle user logout
    """
    # Clear session data
    if 'user_id' in request.session:
        del request.session['user_id']
    if 'username' in request.session:
        del request.session['username']
    if 'is_authenticated' in request.session:
        del request.session['is_authenticated']
    
    messages.success(request, 'You have been logged out successfully')
    return redirect('dashboard:login')

@login_required
def dashboard_home(request):
    """
    Main dashboard view
    """
    # Get user from session
    user_id = request.session.get('user_id')
    if user_id:
        try:
            user = Dashboard.objects.get(id=user_id)
        except Dashboard.DoesNotExist:
            messages.error(request, 'User not found. Please login again.')
            return redirect('dashboard:login')
    else:
        messages.error(request, 'Please login to access the dashboard.')
        return redirect('dashboard:login')
    
    context = {
        'user': user
    }
    return render(request, 'dashboard/index.html', context)


def testimonial_management(request):
    """
    Testimonial management view
    """
    # Verify user exists
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Please login to access this page.')
        return redirect('dashboard:login')
    
    try:
        user = Dashboard.objects.get(id=user_id)  # Verify user exists
        
        # Handle DELETE request for testimonial deletion
        if request.method == 'POST' and request.POST.get('action') == 'delete':
            testimonial_id = request.POST.get('testimonial_id')
            try:
                testimonial = Testimonial.objects.get(id=testimonial_id)
                testimonial_name = testimonial.name
                testimonial.delete()
                messages.success(request, f'Testimonial "{testimonial_name}" deleted successfully!')
            except Testimonial.DoesNotExist:
                messages.error(request, 'Testimonial not found.')
            return redirect('dashboard:testimonial_management')
        
        # Handle toggle active status
        if request.method == 'POST' and request.POST.get('action') == 'toggle_active':
            testimonial_id = request.POST.get('testimonial_id')
            try:
                testimonial = Testimonial.objects.get(id=testimonial_id)
                testimonial.is_active = not testimonial.is_active
                testimonial.save()
                status = "activated" if testimonial.is_active else "deactivated"
                messages.success(request, f'Testimonial "{testimonial.name}" {status} successfully!')
            except Testimonial.DoesNotExist:
                messages.error(request, 'Testimonial not found.')
            return redirect('dashboard:testimonial_management')
        
        testimonials = Testimonial.objects.all().order_by('-created_at')
        
        context = {
            'testimonials': testimonials,
            'user': user
        }
        return render(request, 'dashboard/testimonial_management.html', context)
    except Dashboard.DoesNotExist:
        messages.error(request, 'User not found. Please login again.')
        return redirect('dashboard:login')

def get_testimonials(request):
    """
    API endpoint to get all active testimonials
    GET /api/testimonials/ - API response for API calls
    GET /api/testimonials/ - Show API interface if accessed via browser
    """
    # Check if this is an API request (expects JSON) or a browser request
    is_browser_request = request.META.get('HTTP_ACCEPT', '').find('text/html') >= 0 or \
                    'Mozilla' in request.META.get('HTTP_USER_AGENT', '') or \
                    request.GET.get('format') == 'interface'
    
    if is_browser_request:
        # This is a browser request, show the API interface
        user_id = request.session.get('user_id')
        if user_id:
            try:
                user = Dashboard.objects.get(id=user_id)
                context = {
                    'user': user
                }
                return render(request, 'testimonials_api_interface.html', context)
            except Dashboard.DoesNotExist:
                messages.error(request, 'User not found. Please login again.')
                return redirect('dashboard:login')
        else:
            messages.error(request, 'Please login to access this page.')
            return redirect('dashboard:login')
    else:
        # This is an API request, return JSON
        if request.method == 'GET':
            try:
                testimonials = Testimonial.objects.filter(is_active=True).order_by('-created_at')
                
                # Serialize the data
                serializer = TestimonialSerializer(testimonials, many=True)
                
                # Create response data
                response_data = {
                    'success': True,
                    'testimonials': serializer.data,
                    'count': len(serializer.data)
                }
                
                # Serialize response
                response_serializer = TestimonialListResponseSerializer(data=response_data)
                if response_serializer.is_valid():
                    return JsonResponse(response_serializer.data)
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'Serialization error'
                    }, status=500)
                    
            except Exception as e:
                error_response = {
                    'success': False,
                    'error': str(e)
                }
                error_serializer = APIResponseSerializer(data=error_response)
                if error_serializer.is_valid():
                    return JsonResponse(error_serializer.data, status=500)
                else:
                    return JsonResponse({'success': False, 'error': str(e)}, status=500)
        
        # Method not allowed
        error_response = {
            'success': False,
            'error': 'Method not allowed'
        }
        error_serializer = APIResponseSerializer(data=error_response)
        if error_serializer.is_valid():
            return JsonResponse(error_serializer.data, status=405)
        else:
            return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)



@custom_login_required
@csrf_exempt
def create_testimonial(request):
    """
    API endpoint to create a new testimonial (admin only)
    GET /api/testimonial/ - Show API interface for admin to submit testimonials
    POST /api/testimonial/ - Create a new testimonial via API
    """
    if request.method == 'GET':
        # Display API interface for admin users to submit testimonials
        user_id = request.session.get('user_id')
        if user_id:
            try:
                user = Dashboard.objects.get(id=user_id)
                context = {
                    'user': user
                }
                return render(request, 'testimonial_api_interface.html', context)
            except Dashboard.DoesNotExist:
                messages.error(request, 'User not found. Please login again.')
                return redirect('dashboard:login')
        else:
            messages.error(request, 'Please login to access this page.')
            return redirect('dashboard:login')
    
    elif request.method == 'POST':
        try:
            # Handle both JSON and form data
            if request.content_type == 'application/json':
                try:
                    data = json.loads(request.body)
                except json.JSONDecodeError:
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid JSON data'
                    }, status=400)
            else:
                data = request.POST.dict()
                # Handle file upload
                if request.FILES.get('image'):
                    data['image'] = request.FILES['image']
            
            # Serialize and validate the data
            serializer = TestimonialCreateSerializer(data=data)
            
            if serializer.is_valid():
                # Save the testimonial
                testimonial = serializer.save()
                
                # Serialize the created testimonial
                testimonial_serializer = TestimonialSerializer(testimonial)
                
                # Create success response
                response_data = {
                    'success': True,
                    'message': 'Testimonial created successfully',
                    'testimonial': testimonial_serializer.data
                }
                
                response_serializer = TestimonialCreateResponseSerializer(data=response_data)
                if response_serializer.is_valid():
                    return JsonResponse(response_serializer.data, status=201)
                else:
                    return JsonResponse({
                        'success': True,
                        'message': 'Testimonial created successfully',
                        'testimonial': testimonial_serializer.data
                    }, status=201)
            else:
                # Validation failed
                error_response = {
                    'success': False,
                    'error': 'Validation failed',
                    'details': serializer.errors
                }
                error_serializer = APIResponseSerializer(data=error_response)
                if error_serializer.is_valid():
                    return JsonResponse(error_serializer.data, status=400)
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'Validation failed',
                        'details': serializer.errors
                    }, status=400)
                    
        except Exception as e:
            error_response = {
                'success': False,
                'error': str(e)
            }
            error_serializer = APIResponseSerializer(data=error_response)
            if error_serializer.is_valid():
                return JsonResponse(error_serializer.data, status=500)
            else:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    # Method not allowed
    error_response = {
        'success': False,
        'error': 'Method not allowed'
    }
    error_serializer = APIResponseSerializer(data=error_response)
    if error_serializer.is_valid():
        return JsonResponse(error_serializer.data, status=405)
    else:
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

def enquiry_management(request):
    """
    Enquiry management view
    """
    # Verify user exists
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Please login to access this page.')
        return redirect('dashboard:login')
    
    try:
        user = Dashboard.objects.get(id=user_id)  # Verify user exists
        
        # Handle DELETE request for enquiry deletion
        if request.method == 'POST' and request.POST.get('action') == 'delete':
            enquiry_id = request.POST.get('enquiry_id')
            try:
                enquiry = Enquiry.objects.get(id=enquiry_id)
                enquiry_subject = enquiry.subject
                enquiry.delete()
                messages.success(request, f'Enquiry "{enquiry_subject}" deleted successfully!')
            except Enquiry.DoesNotExist:
                messages.error(request, 'Enquiry not found.')
            return redirect('dashboard:enquiry_management')
        
        enquiries = Enquiry.objects.all().order_by('-created_at')
        
        context = {
            'enquiries': enquiries,
            'user': user
        }
        return render(request, 'dashboard/enquiry_management.html', context)
    except Dashboard.DoesNotExist:
        messages.error(request, 'User not found. Please login again.')
        return redirect('dashboard:login')

def client_logo_management(request, **kwargs):
    """
    Client logo management view
    """
    import os
    import json
    import uuid
    from django.conf import settings
    
    # Handle POST request for logo upload
    if request.method == 'POST':
        client_name = request.POST.get('client_name')
        client_email = request.POST.get('client_email', '')
        client_phone = request.POST.get('client_phone', '')
        client_company = request.POST.get('company_name', '')
        description = request.POST.get('description', '')
        
        # Handle file upload
        if 'logo_file' in request.FILES:
            logo_file = request.FILES['logo_file']
            
            # Create the client_logos directory inside the dashboard app's media folder if it doesn't exist
            client_logos_path = os.path.join(settings.BASE_DIR, 'dashboard', 'media', 'client_logos')
            os.makedirs(client_logos_path, exist_ok=True)
            
            # Create a safe filename
            file_extension = os.path.splitext(logo_file.name)[1]
            safe_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Save the file to the client_logos directory
            file_path = os.path.join(client_logos_path, safe_filename)
            
            with open(file_path, 'wb+') as destination:
                for chunk in logo_file.chunks():
                    destination.write(chunk)
            
            # Construct the relative path to save in the database (for later retrieval)
            relative_path = f"dashboard/media/client_logos/{safe_filename}"
            
            # Store client data in session
            clients_data = request.session.get('clients_data', [])
            
            # Check if client already exists and update, otherwise add new
            client_found = False
            for client in clients_data:
                if client['name'].lower() == client_name.lower():
                    client['email'] = client_email
                    client['phone'] = client_phone
                    client['company'] = client_company
                    client['logo_path'] = relative_path
                    client['updated_at'] = timezone.now().isoformat()
                    client_found = True
                    break
            
            if not client_found:
                # Add new client
                new_client = {
                    'id': str(uuid.uuid4()),
                    'name': client_name,
                    'email': client_email,
                    'phone': client_phone,
                    'company': client_company,
                    'logo_path': relative_path,
                    'created_at': timezone.now().isoformat(),
                    'updated_at': timezone.now().isoformat()
                }
                clients_data.append(new_client)
            
            request.session['clients_data'] = clients_data
            
            messages.success(request, f'Client logo for "{client_name}" uploaded successfully!')
        else:
            messages.error(request, 'Please select a logo file to upload.')
        
        return redirect('dashboard:client_logo_management')
    
    # Handle DELETE request for deleting a client
    elif request.method == 'DELETE':
        import json
        try:
            data = json.loads(request.body)
            client_id = data.get('client_id')
            
            clients_data = request.session.get('clients_data', [])
            clients_data = [client for client in clients_data if client['id'] != client_id]
            request.session['clients_data'] = clients_data
            
            return JsonResponse({'success': True, 'message': 'Client deleted successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # Handle GET request for viewing client details
    elif request.method == 'GET' and (request.GET.get('action') == 'view' or 'client_id' in kwargs):
        client_id = request.GET.get('client_id') or kwargs.get('client_id')
        if client_id:
            clients_data = request.session.get('clients_data', [])
            client = next((c for c in clients_data if c['id'] == str(client_id)), None)
            if client:
                # Ensure the client has a company field (for backward compatibility)
                if 'company' not in client:
                    client['company'] = ''
                
                context = {
                    'client': client,
                    'current_page': 'client_logo_management'
                }
                return render(request, 'dashboard/client_detail.html', context)
            else:
                messages.error(request, 'Client not found')
                return redirect('dashboard:client_logo_management')
    
    # Handle GET request for editing client details (via URL parameter)
    elif request.method == 'GET' and kwargs.get('client_id'):
        client_id = kwargs.get('client_id')
        if client_id:
            clients_data = request.session.get('clients_data', [])
            client = next((c for c in clients_data if c['id'] == str(client_id)), None)
            if client:
                # Ensure the client has a company field (for backward compatibility)
                if 'company' not in client:
                    client['company'] = ''
                
                context = {
                    'client': client,
                    'current_page': 'client_logo_management'
                }
                return render(request, 'dashboard/client_edit.html', context)
            else:
                messages.error(request, 'Client not found')
                return redirect('dashboard:client_logo_management')
    
    # Handle GET request for editing client details (via query parameter - legacy support)
    elif request.method == 'GET' and request.GET.get('action') == 'edit':
        client_id = request.GET.get('client_id')
        if client_id:
            clients_data = request.session.get('clients_data', [])
            client = next((c for c in clients_data if c['id'] == str(client_id)), None)
            if client:
                # Ensure the client has a company field (for backward compatibility)
                if 'company' not in client:
                    client['company'] = ''
                
                context = {
                    'client': client,
                    'current_page': 'client_logo_management'
                }
                return render(request, 'dashboard/client_edit.html', context)
            else:
                messages.error(request, 'Client not found')
                return redirect('dashboard:client_logo_management')
    
    # Handle POST request for updating client details
    elif request.method == 'POST' and request.POST.get('action') == 'update':
        client_id = request.POST.get('client_id')
        client_name = request.POST.get('client_name')
        client_email = request.POST.get('client_email')
        client_phone = request.POST.get('client_phone')
        client_company = request.POST.get('company_name')
        
        if client_id and client_name:
            clients_data = request.session.get('clients_data', [])
            for client in clients_data:
                if client['id'] == client_id:
                    client['name'] = client_name
                    client['email'] = client_email
                    client['phone'] = client_phone
                    client['company'] = client_company
                    client['updated_at'] = timezone.now().isoformat()
                    
                    # Handle logo file upload if provided
                    if 'logo_file' in request.FILES:
                        logo_file = request.FILES['logo_file']
                        import os
                        import uuid
                        from django.conf import settings
                        
                        # Create the client_logos directory inside the dashboard app's media folder if it doesn't exist
                        client_logos_path = os.path.join(settings.BASE_DIR, 'dashboard', 'media', 'client_logos')
                        os.makedirs(client_logos_path, exist_ok=True)
                        
                        # Create a safe filename
                        file_extension = os.path.splitext(logo_file.name)[1]
                        safe_filename = f"{uuid.uuid4()}{file_extension}"
                        
                        # Save the file to the client_logos directory
                        file_path = os.path.join(client_logos_path, safe_filename)
                        
                        with open(file_path, 'wb+') as destination:
                            for chunk in logo_file.chunks():
                                destination.write(chunk)
                        
                        # Update the logo path
                        client['logo_path'] = f"dashboard/media/client_logos/{safe_filename}"
                    
                    break
            
            request.session['clients_data'] = clients_data
            messages.success(request, 'Client details updated successfully')
            return redirect('dashboard:client_logo_management')
        else:
            messages.error(request, 'Client name is required')
            return redirect(f'{request.path}?action=edit&client_id={client_id}')
    
    # For GET request, render the management page
    # Retrieve client data from session
    clients_data = request.session.get('clients_data', [])
    
    # Ensure all clients have the company field (for backward compatibility)
    modified = False
    for client in clients_data:
        if 'company' not in client:
            client['company'] = ''
            modified = True
    
    # If we modified the data, save it back to the session
    if modified:
        request.session['clients_data'] = clients_data
    
    context = {
        'current_page': 'client_logo_management',
        'clients_data': clients_data
    }
    return render(request, 'dashboard/client_logo_management.html', context)

@login_required
def global_settings(request):
    """
    Global settings management view
    """
    # Verify user exists
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Please login to access this page.')
        return redirect('dashboard:login')
    
    try:
        user = Dashboard.objects.get(id=user_id)  # Verify user exists
        settings = GlobalSetting.objects.all()
        
        context = {
            'settings': settings,
            'user': user,
            'current_page': 'global_settings'
        }
        return render(request, 'global_settings.html', context)
    except Dashboard.DoesNotExist:
        messages.error(request, 'User not found. Please login again.')
        return redirect('dashboard:login')


@login_required
def user_profile(request):
    """
    View user profile
    """
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Please login to access this page.')
        return redirect('dashboard:login')
    
    try:
        user = Dashboard.objects.get(id=user_id)
        context = {
            'user': user
        }
        return render(request, 'profile.html', context)
    except Dashboard.DoesNotExist:
        messages.error(request, 'User not found. Please login again.')
        return redirect('dashboard:login')

@login_required
def user_list(request):
    """
    List all dashboard users
    """
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Please login to access this page.')
        return redirect('dashboard:login')
    
    try:
        Dashboard.objects.get(id=user_id)  # Verify current user exists
        users = Dashboard.objects.all()
        context = {
            'users': users
        }
        return render(request, 'user_list.html', context)
    except Dashboard.DoesNotExist:
        messages.error(request, 'User not found. Please login again.')
        return redirect('dashboard:login')

@login_required
def user_detail(request, user_id):
    """
    View details for a specific user
    """
    # Verify current user exists
    current_user_id = request.session.get('user_id')
    if not current_user_id:
        messages.error(request, 'Please login to access this page.')
        return redirect('dashboard:login')
    
    try:
        Dashboard.objects.get(id=current_user_id)  # Verify current user exists
        
        # Get the requested user
        user = Dashboard.objects.get(id=user_id)
        context = {
            'user': user
        }
        return render(request, 'user_detail.html', context)
    except Dashboard.DoesNotExist:
        messages.error(request, 'User not found. Please login again.')
        return redirect('dashboard:login')

@csrf_exempt
@login_required
def create_user(request):
    if request.method == 'POST':
        # ... validation logic ...
        if serializer.is_valid():
            user = serializer.save()
            # Return 201 Created with the created resource
            return JsonResponse({
                'success': True,
                'message': 'User created successfully',
                'user': {
                    'id': str(user.id),
                    'username': user.username,
                    'email': user.email
                }
            }, status=status.HTTP_201_CREATED)  # This ensures 201 status

@login_required
def base(request):
    """
    Base view for the dashboard
    """
    # Get user from session
    user_id = request.session.get('user_id')
    if user_id:
        try:
            user = Dashboard.objects.get(id=user_id)
            context = {
                'user': user
            }
            return render(request, 'dashboard/skeleton.html', context)
        except Dashboard.DoesNotExist:
            # If user doesn't exist, redirect to login
            messages.error(request, 'User not found. Please login again.')
            return redirect('dashboard:login')
    else:
        # If no user_id in session, redirect to login
        messages.error(request, 'Please login to access the dashboard.')
        return redirect('dashboard:login')

def index(request):
    """
    Index page view
    """
    # Verify user exists
    user_id = request.session.get('user_id')
    if user_id:
        try:
            user = Dashboard.objects.get(id=user_id)
            context = {
                'user': user,
                'current_page': 'dashboard'
            }
            return render(request, 'dashboard/index.html', context)
        except Dashboard.DoesNotExist:
            messages.error(request, 'User not found. Please login again.')
            return redirect('dashboard:login')
    else:
        messages.error(request, 'Please login to access this page.')
        return redirect('dashboard:login')

def add_testimonial(request):
    """
    View to add testimonials via form interface
    """
    user_id = request.session.get('user_id')
    if user_id:
        try:
            user = Dashboard.objects.get(id=user_id)
            context = {
                'user': user
            }
            return render(request, 'testimonials/add.html', context)
        except Dashboard.DoesNotExist:
            messages.error(request, 'User not found. Please login again.')
            return redirect('dashboard:login')
    else:
        messages.error(request, 'Please login to access this page.')
        return redirect('dashboard:login')

def view_testimonial(request, pk):
    """
    View to display a single testimonial
    """
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Please login to access this page.')
        return redirect('dashboard:login')
    
    try:
        user = Dashboard.objects.get(id=user_id)
        testimonial = Testimonial.objects.get(pk=pk)
        
        context = {
            'testimonial': testimonial,
            'user': user
        }
        return render(request, 'testimonials/view.html', context)
    except Dashboard.DoesNotExist:
        messages.error(request, 'User not found. Please login again.')
        return redirect('dashboard:login')
    except Testimonial.DoesNotExist:
        messages.error(request, 'Testimonial not found.')
        return redirect('dashboard:testimonial_management')

def edit_testimonial(request, pk):
    """
    View to edit an existing testimonial
    """
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Please login to access this page.')
        return redirect('dashboard:login')
    
    try:
        user = Dashboard.objects.get(id=user_id)
        testimonial = Testimonial.objects.get(pk=pk)
        
        if request.method == 'POST':
            # Update testimonial with form data
            testimonial.name = request.POST.get('name', testimonial.name)
            testimonial.designation = request.POST.get('designation', testimonial.designation)
            testimonial.company = request.POST.get('company', testimonial.company)
            testimonial.message = request.POST.get('message', testimonial.message)
            testimonial.rating = int(request.POST.get('rating', testimonial.rating))
            testimonial.is_active = request.POST.get('is_active', 'false') == 'true'
            
            # Handle image upload if provided
            if 'image' in request.FILES:
                testimonial.image = request.FILES['image']
            elif request.POST.get('clear_image') == 'true':
                # Clear the image if the clear_image flag is set
                testimonial.image = None
            
            testimonial.save()
            messages.success(request, 'Testimonial updated successfully!')
            return redirect('dashboard:testimonial_management')
        
        context = {
            'testimonial': testimonial,
            'user': user
        }
        return render(request, 'testimonials/edit.html', context)
    except Dashboard.DoesNotExist:
        messages.error(request, 'User not found. Please login again.')
        return redirect('dashboard:login')
    except Testimonial.DoesNotExist:
        messages.error(request, 'Testimonial not found.')
        return redirect('dashboard:testimonial_management')


def delete_testimonial(request, pk):
    """
    Handle deleting testimonial
    """
    # Check if user is authenticated using session
    if not request.session.get('is_authenticated'):
        # Store the next URL to redirect after login
        request.session['next_url'] = request.get_full_path()
        return redirect('dashboard:login')
    
    from .models import Testimonial
    try:
        testimonial = Testimonial.objects.get(id=pk)
        testimonial.delete()
        messages.success(request, 'Testimonial deleted successfully!')
    except Testimonial.DoesNotExist:
        messages.error(request, 'Testimonial not found')
    
    return redirect('dashboard:testimonial_list')


def testimonial_list(request):
    """
    View to display list of testimonials
    """
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Please login to access this page.')
        return redirect('dashboard:login')
    
    try:
        user = Dashboard.objects.get(id=user_id)
        testimonials = Testimonial.objects.all().order_by('-created_at')
        
        context = {
            'testimonials': testimonials,
            'user': user,
            'current_page': 'testimonials'
        }
        return render(request, 'testimonials/list.html', context)
    except Dashboard.DoesNotExist:
        messages.error(request, 'User not found. Please login again.')
        return redirect('dashboard:login')


def update_testimonial_api(request, pk):
    """
    API endpoint to update a testimonial
    """
    if request.method == 'PUT':
        try:
            import json
            data = json.loads(request.body)
            
            testimonial = Testimonial.objects.get(pk=pk)
            testimonial.name = data.get('name', testimonial.name)
            testimonial.designation = data.get('designation', testimonial.designation)
            testimonial.company = data.get('company', testimonial.company)
            testimonial.message = data.get('message', testimonial.message)
            testimonial.rating = data.get('rating', testimonial.rating)
            testimonial.is_active = data.get('is_active', testimonial.is_active)
            
            testimonial.save()
            
            # Serialize the updated testimonial
            serialized_testimonial = {
                'id': str(testimonial.id),
                'name': testimonial.name,
                'designation': testimonial.designation,
                'company': testimonial.company,
                'message': testimonial.message,
                'rating': testimonial.rating,
                'is_active': testimonial.is_active,
                'created_at': testimonial.created_at.isoformat()
            }
            
            return JsonResponse({
                'success': True,
                'message': 'Testimonial updated successfully',
                'testimonial': serialized_testimonial
            })
        except Testimonial.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Testimonial not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def enquiry_list(request):
    """
    View for listing enquiries
    """
    return render(request, 'enquiry.html')

def blog_list(request):
    """
    View for listing blogs
    """
    return render(request, 'blogs/list.html')

def blog_add(request):
    """
    View for adding a new blog
    """
    return render(request, 'blogs/add.html')

def blog_view(request):
    """
    View for viewing blog details
    """
    return render(request, 'blogs/view.html')

def payment_history(request):
    """
    View for payment history
    """
    return render(request, 'payment.html')

def token_management(request):
    """
    View for token management
    """
    return render(request, 'token.html')

def lead_management(request):
    """
    View for lead management
    """
    return render(request, 'lead.html')

def matching_engine(request):
    """
    View for matching engine
    """
    return render(request, 'matchengine.html')



@api_view(['POST'])
@permission_classes([AllowAny])
def get_jwt_token(request):
    """
    API endpoint to get JWT tokens for user authentication
    Expected payload: {"email": "user@example.com", "password": "password"}
    Returns: {"access": "access_token", "refresh": "refresh_token", "user_id": id, "email": "user@example.com"}
    """
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return JsonResponse({
            'success': False,
            'error': 'Email and password are required'
        }, status=400)

    try:
        # Find user by email
        user = Dashboard.objects.get(email__iexact=email)
        
        # Check if user is active
        if not user.is_active:
            return JsonResponse({
                'success': False,
                'error': 'Account is deactivated'
            }, status=401)
        
        # Verify password
        if user.check_password(password):
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return JsonResponse({
                'success': True,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user_id': str(user.id),
                'email': user.email,
                'username': user.username,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Invalid email or password'
            }, status=401)
            
    except Dashboard.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Invalid email or password'
        }, status=401)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_jwt_token(request):
    """
    API endpoint to refresh JWT access token using refresh token
    Expected payload: {"refresh": "refresh_token"}
    Returns: {"access": "new_access_token"}
    """
    refresh_token = request.data.get('refresh')

    if not refresh_token:
        return JsonResponse({
            'success': False,
            'error': 'Refresh token is required'
        }, status=400)

    try:
        # Verify refresh token and generate new access token
        from rest_framework_simplejwt.tokens import RefreshToken
        token = RefreshToken(refresh_token)
        new_access_token = str(token.access_token)
        
        return JsonResponse({
            'success': True,
            'access': new_access_token
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Invalid or expired refresh token'
        }, status=401)


def dashboard_settings(request):
    """
    Dashboard settings page for customizing dashboard appearance and preferences
    """
    if request.method == 'POST':
        # Handle form submissions
        # This would typically save settings to database
        messages.success(request, 'Settings saved successfully!')
        return redirect('dashboard:dashboard_settings')
    
    context = {
        'current_page': 'dashboard_settings',
    }
    return render(request, 'dashboard/dashboard_settings.html', context)


@csrf_exempt
def api_dashboard_list(request):
    """GET /api/dashboard/users/ - List all dashboard users"""
    if request.method == 'GET':
        users = Dashboard.objects.all().order_by('-created_at')
        serializer = DashboardSerializer(users, many=True)
        
        response_data = {
            'success': True,
            'count': users.count(),
            'users': serializer.data
        }
        
        response_serializer = DashboardListResponseSerializer(data=response_data)
        if response_serializer.is_valid():
            return JsonResponse(response_serializer.data)
        else:
            return JsonResponse(response_data)


@csrf_exempt
def api_dashboard_create(request):
    """POST /api/dashboard/users/create/ - Create new dashboard user"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            serializer = DashboardCreateSerializer(data=data)
            
            if serializer.is_valid():
                user = serializer.save()
                user_serializer = DashboardSerializer(user)
                
                response_data = {
                    'success': True,
                    'message': 'User created successfully',
                    'user': user_serializer.data
                }
                
                response_serializer = DashboardCreateResponseSerializer(data=response_data)
                if response_serializer.is_valid():
                    return JsonResponse(response_serializer.data, status=201)
                else:
                    return JsonResponse({
                        'success': True,
                        'message': 'User created successfully',
                        'user': user_serializer.data
                    }, status=201)
            else:
                error_response = {
                    'success': False,
                    'error': 'Validation failed',
                    'details': serializer.errors
                }
                return JsonResponse(error_response, status=400)
                
        except Exception as e:
            error_response = {
                'success': False,
                'error': str(e)
            }
            return JsonResponse(error_response, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_testimonials_list(request):
    """GET /api/dashboard/testimonials/ - List all testimonials"""
    if request.method == 'GET':
        testimonials = Testimonial.objects.all().order_by('-created_at')
        serializer = TestimonialSerializer(testimonials, many=True)
        
        response_data = {
            'success': True,
            'count': testimonials.count(),
            'testimonials': serializer.data
        }
        
        response_serializer = TestimonialListResponseSerializer(data=response_data)
        if response_serializer.is_valid():
            return JsonResponse(response_serializer.data)
        else:
            return JsonResponse(response_data)


@csrf_exempt
def api_testimonial_create(request):
    """POST /api/dashboard/testimonials/create/ - Create new testimonial"""
    if request.method == 'POST':
        try:
            if request.content_type.startswith('multipart/form-data') or request.content_type.startswith('application/x-www-form-urlencoded'):
                # Handle form data (including file uploads)
                data = {}
                for key in request.POST:
                    data[key] = request.POST[key]
                
                # Convert boolean fields
                if 'is_active' in data:
                    data['is_active'] = data['is_active'] in ['true', '1', 'on', 'yes']
                
                # Convert numeric fields
                if 'rating' in data:
                    try:
                        data['rating'] = int(data['rating'])
                    except ValueError:
                        data['rating'] = 5  # default value
                
                # Prepare files data
                files = {}
                for key in request.FILES:
                    files[key] = request.FILES[key]
                
                # Combine data and files
                all_data = {}
                all_data.update(data)
                all_data.update(files)
                
                serializer = TestimonialCreateSerializer(data=all_data)
            else:
                # Handle JSON data
                data = json.loads(request.body)
                serializer = TestimonialCreateSerializer(data=data)
            
            if serializer.is_valid():
                testimonial = serializer.save()
                testimonial_serializer = TestimonialSerializer(testimonial)
                
                response_data = {
                    'success': True,
                    'message': 'Testimonial created successfully',
                    'testimonial': testimonial_serializer.data
                }
                
                response_serializer = TestimonialCreateResponseSerializer(data=response_data)
                if response_serializer.is_valid():
                    return JsonResponse(response_serializer.data, status=201)
                else:
                    return JsonResponse({
                        'success': True,
                        'message': 'Testimonial created successfully',
                        'testimonial': testimonial_serializer.data
                    }, status=201)
            else:
                error_response = {
                    'success': False,
                    'error': 'Validation failed',
                    'details': serializer.errors
                }
                return JsonResponse(error_response, status=400)
                
        except json.JSONDecodeError:
            error_response = {
                'success': False,
                'error': 'Invalid JSON data'
            }
            return JsonResponse(error_response, status=400)
        except Exception as e:
            error_response = {
                'success': False,
                'error': str(e)
            }
            return JsonResponse(error_response, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_enquiries_list(request):
    """GET /api/dashboard/enquiries/ - List all enquiries"""
    if request.method == 'GET':
        enquiries = Enquiry.objects.all().order_by('-created_at')
        serializer = EnquirySerializer(enquiries, many=True)
        
        response_data = {
            'success': True,
            'count': enquiries.count(),
            'enquiries': serializer.data
        }
        
        response_serializer = EnquiryListResponseSerializer(data=response_data)
        if response_serializer.is_valid():
            return JsonResponse(response_serializer.data)
        else:
            return JsonResponse(response_data)


@csrf_exempt
def api_enquiry_create(request):
    """POST /api/dashboard/enquiries/create/ - Create new enquiry"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            serializer = EnquiryCreateSerializer(data=data)
            
            if serializer.is_valid():
                enquiry = serializer.save()
                enquiry_serializer = EnquirySerializer(enquiry)
                
                response_data = {
                    'success': True,
                    'message': 'Enquiry created successfully',
                    'enquiry': enquiry_serializer.data
                }
                
                response_serializer = EnquiryCreateResponseSerializer(data=response_data)
                if response_serializer.is_valid():
                    return JsonResponse(response_serializer.data, status=201)
                else:
                    return JsonResponse({
                        'success': True,
                        'message': 'Enquiry created successfully',
                        'enquiry': enquiry_serializer.data
                    }, status=201)
            else:
                error_response = {
                    'success': False,
                    'error': 'Validation failed',
                    'details': serializer.errors
                }
                return JsonResponse(error_response, status=400)
                
        except Exception as e:
            error_response = {
                'success': False,
                'error': str(e)
            }
            return JsonResponse(error_response, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_settings_list(request):
    """GET /api/dashboard/settings/ - List all global settings"""
    if request.method == 'GET':
        settings = GlobalSetting.objects.all().order_by('key')
        serializer = GlobalSettingSerializer(settings, many=True)
        
        response_data = {
            'success': True,
            'count': settings.count(),
            'settings': serializer.data
        }
        
        response_serializer = GlobalSettingListResponseSerializer(data=response_data)
        if response_serializer.is_valid():
            return JsonResponse(response_serializer.data)
        else:
            return JsonResponse(response_data)


@csrf_exempt
def api_setting_create(request):
    """POST /api/dashboard/settings/create/ - Create new global setting"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            serializer = GlobalSettingCreateSerializer(data=data)
            
            if serializer.is_valid():
                setting = serializer.save()
                setting_serializer = GlobalSettingSerializer(setting)
                
                response_data = {
                    'success': True,
                    'message': 'Setting created successfully',
                    'setting': setting_serializer.data
                }
                
                response_serializer = GlobalSettingCreateResponseSerializer(data=response_data)
                if response_serializer.is_valid():
                    return JsonResponse(response_serializer.data, status=201)
                else:
                    return JsonResponse({
                        'success': True,
                        'message': 'Setting created successfully',
                        'setting': setting_serializer.data
                    }, status=201)
            else:
                error_response = {
                    'success': False,
                    'error': 'Validation failed',
                    'details': serializer.errors
                }
                return JsonResponse(error_response, status=400)
                
        except Exception as e:
            error_response = {
                'success': False,
                'error': str(e)
            }
            return JsonResponse(error_response, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


