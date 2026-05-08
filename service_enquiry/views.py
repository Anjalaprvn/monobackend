from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ServiceEnquiry
from .serializers import (
    ServiceEnquirySerializer, ServiceEnquiryCreateSerializer,
    ServiceEnquiryListResponseSerializer, ServiceEnquiryCreateResponseSerializer, APIResponseSerializer
)
import json
import uuid


def enquiry_list_html(request):
    """
    HTML view to display list of service enquiries
    """
    enquiries = ServiceEnquiry.objects.all().order_by('-created_at')
    context = {
        'enquiries': enquiries,
        'app_name': 'service_enquiry',
        'model_name': 'ServiceEnquiry',
        'current_page': 'enquiry_management'
    }
    return render(request, 'service_enquiry/list.html', context)


def enquiry_add_html(request):
    """
    HTML view to add a new service enquiry
    """
    from services.models import Service
    services = Service.objects.all().order_by('name')
    
    context = {
        'app_name': 'service_enquiry',
        'model_name': 'ServiceEnquiry',
        'services': services
    }
    return render(request, 'service_enquiry/add.html', context)


def enquiry_detail_html(request, pk):
    """
    HTML view to display details of a specific service enquiry
    """
    try:
        enquiry = ServiceEnquiry.objects.get(pk=pk)
        context = {
            'enquiry': enquiry,
            'app_name': 'service_enquiry',
            'model_name': 'ServiceEnquiry'
        }
        return render(request, 'service_enquiry/view.html', context)
    except ServiceEnquiry.DoesNotExist:
        from django.http import Http404
        raise Http404("Service Enquiry does not exist")


def enquiry_edit_html(request, pk):
    """
    HTML view to edit a specific service enquiry
    """
    try:
        enquiry = ServiceEnquiry.objects.get(pk=pk)
        context = {
            'enquiry': enquiry,
            'app_name': 'service_enquiry',
            'model_name': 'ServiceEnquiry'
        }
        return render(request, 'service_enquiry/edit.html', context)
    except ServiceEnquiry.DoesNotExist:
        from django.http import Http404
        raise Http404("Service Enquiry does not exist")


@csrf_exempt
def update_enquiry(request, pk):
    """
    PUT /api/enquiries/{id}/update/ - updates an existing service enquiry
    """
    if request.method == 'PUT':
        try:
            enquiry = ServiceEnquiry.objects.get(pk=pk)
            
            if request.content_type.startswith('multipart/form-data') or request.content_type.startswith('application/x-www-form-urlencoded'):
                # Handle form data
                data = {}
                for key in request.POST:
                    data[key] = request.POST[key]
                
                # Convert service ID to UUID object if provided
                if 'service' in data and data['service']:
                    from uuid import UUID
                    try:
                        data['service'] = UUID(data['service'])
                    except ValueError:
                        pass  # Let serializer handle the validation
                
                serializer = ServiceEnquiryCreateSerializer(enquiry, data=data, partial=True)
            else:
                # Handle JSON data
                data = json.loads(request.body)
                serializer = ServiceEnquiryCreateSerializer(enquiry, data=data, partial=True)
            
            if serializer.is_valid():
                updated_enquiry = serializer.save()
                enquiry_serializer = ServiceEnquirySerializer(updated_enquiry)
                
                response_data = {
                    'success': True,
                    'message': 'Service enquiry updated successfully',
                    'enquiry': enquiry_serializer.data
                }
                
                response_serializer = ServiceEnquiryCreateResponseSerializer(data=response_data)
                if response_serializer.is_valid():
                    return JsonResponse(response_serializer.data)
                else:
                    return JsonResponse({
                        'success': True,
                        'message': 'Service enquiry updated successfully',
                        'enquiry': enquiry_serializer.data
                    })
            else:
                error_response = {
                    'success': False,
                    'error': 'Validation failed',
                    'details': serializer.errors
                }
                return JsonResponse(error_response, status=400)
                
        except ServiceEnquiry.DoesNotExist:
            error_response = {
                'success': False,
                'error': 'Service enquiry not found'
            }
            return JsonResponse(error_response, status=404)
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
def delete_enquiry(request, pk):
    """
    POST /service_enquiry/<uuid:pk>/delete/ - deletes an existing service enquiry
    """
    if request.method == 'POST':
        try:
            enquiry = ServiceEnquiry.objects.get(pk=pk)
            enquiry.delete()
            
            # Redirect back to the enquiry list page after successful deletion
            from django.shortcuts import redirect
            return redirect('service_enquiry:enquiry_list')
                
        except ServiceEnquiry.DoesNotExist:
            # Even if enquiry doesn't exist, redirect back to the list page
            from django.shortcuts import redirect
            return redirect('service_enquiry:enquiry_list')
        except Exception as e:
            # On any error, redirect back to the list page
            from django.shortcuts import redirect
            return redirect('service_enquiry:enquiry_list')
    
    # If not a POST request, redirect back to the list page
    from django.shortcuts import redirect
    return redirect('service_enquiry:enquiry_list')


@csrf_exempt
def enquiry_list(request):
    """
    GET /api/enquiries/ - returns JSON list of service enquiries
    """
    if request.method == 'GET':
        enquiries = ServiceEnquiry.objects.all().order_by('-created_at')
        serializer = ServiceEnquirySerializer(enquiries, many=True)
        
        response_data = {
            'success': True,
            'count': enquiries.count(),
            'enquiries': serializer.data
        }
        
        response_serializer = ServiceEnquiryListResponseSerializer(data=response_data)
        if response_serializer.is_valid():
            return JsonResponse(response_serializer.data)
        else:
            return JsonResponse(response_data)


@csrf_exempt
def create_enquiry(request):
    """
    POST /api/enquiries/create/ - creates a new service enquiry
    """
    if request.method == 'POST':
        try:
            if request.content_type.startswith('multipart/form-data') or request.content_type.startswith('application/x-www-form-urlencoded'):
                # Handle form data
                data = {}
                for key in request.POST:
                    data[key] = request.POST[key]
                
                # Convert service ID to UUID object if provided
                if 'service' in data and data['service']:
                    from uuid import UUID
                    try:
                        data['service'] = UUID(data['service'])
                    except ValueError:
                        pass  # Let serializer handle the validation
                
                serializer = ServiceEnquiryCreateSerializer(data=data)
            else:
                # Handle JSON data
                data = json.loads(request.body)
                serializer = ServiceEnquiryCreateSerializer(data=data)
            
            if serializer.is_valid():
                enquiry = serializer.save()
                enquiry_serializer = ServiceEnquirySerializer(enquiry)
                
                response_data = {
                    'success': True,
                    'message': 'Service enquiry created successfully',
                    'enquiry': enquiry_serializer.data
                }
                
                response_serializer = ServiceEnquiryCreateResponseSerializer(data=response_data)
                if response_serializer.is_valid():
                    return JsonResponse(response_serializer.data, status=201)
                else:
                    return JsonResponse({
                        'success': True,
                        'message': 'Service enquiry created successfully',
                        'enquiry': enquiry_serializer.data
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


def api_get_testing(request):
    """
    Redirect to centralized GET API testing page for service_enquiry app
    """
    from django.shortcuts import redirect
    return redirect('/dashboard/api/testing/get/?app=service_enquiry')


def api_post_testing(request):
    """
    Redirect to centralized POST API testing page for service_enquiry app
    """
    from django.shortcuts import redirect
    return redirect('/dashboard/api/testing/post/?app=service_enquiry')