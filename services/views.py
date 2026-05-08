from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Service
from .serializers import (
    ServiceSerializer, ServiceCreateSerializer,
    ServiceListResponseSerializer, ServiceCreateResponseSerializer, APIResponseSerializer
)
import json
import uuid


def service_list_html(request):
    """
    HTML view to display list of services
    """
    services = Service.objects.all().order_by('-created_at')
    context = {
        'services': services,
        'app_name': 'services',
        'model_name': 'Service',
        'current_page': 'services'
    }
    return render(request, 'services/list.html', context)


def service_add_html(request):
    """
    HTML view to add a new service
    """
    context = {
        'app_name': 'services',
        'model_name': 'Service'
    }
    return render(request, 'services/add.html', context)


def service_detail_html(request, pk):
    """
    HTML view to display details of a specific service
    """
    try:
        service = Service.objects.get(pk=pk)
        context = {
            'service': service,
            'app_name': 'services',
            'model_name': 'Service'
        }
        return render(request, 'services/view.html', context)
    except Service.DoesNotExist:
        from django.http import Http404
        raise Http404("Service does not exist")


def service_edit_html(request, pk):
    """
    HTML view to edit a service
    """
    service = get_object_or_404(Service, pk=pk)
    context = {
        'service': service,
        'app_name': 'services',
        'model_name': 'Service'
    }
    return render(request, 'services/edit.html', context)


@csrf_exempt
def update_service(request, pk):
    """
    PUT /api/services/{id}/ - updates an existing service
    """
    if request.method == 'PUT':
        try:
            service = Service.objects.get(pk=pk)
            
            if request.content_type.startswith('multipart/form-data') or request.content_type.startswith('application/x-www-form-urlencoded'):
                # Handle form data (including file uploads)
                data = {}
                for key in request.POST:
                    data[key] = request.POST[key]
                
                # Convert boolean fields
                if 'is_active' in data:
                    data['is_active'] = data['is_active'] in ['true', '1', 'on', 'yes']
                
                # Handle file uploads
                files = {}
                for key in request.FILES:
                    files[key] = request.FILES[key]
                
                # Check if icon should be cleared
                if data.get('clear_icon') == 'true':
                    service.icon = None
                    service.save()
                    
                    # Prepare response data
                    service_serializer = ServiceSerializer(service)
                    response_data = {
                        'success': True,
                        'message': 'Service updated successfully',
                        'service': service_serializer.data
                    }
                    
                    return JsonResponse(response_data)
                
                # Combine data and files for serializer
                all_data = {}
                all_data.update(data)
                all_data.update(files)
                
                serializer = ServiceCreateSerializer(service, data=all_data, partial=True)
            else:
                # Handle JSON data
                data = json.loads(request.body)
                serializer = ServiceCreateSerializer(service, data=data, partial=True)
            
            if serializer.is_valid():
                updated_service = serializer.save()
                service_serializer = ServiceSerializer(updated_service)
                
                response_data = {
                    'success': True,
                    'message': 'Service updated successfully',
                    'service': service_serializer.data
                }
                
                response_serializer = ServiceCreateResponseSerializer(data=response_data)
                if response_serializer.is_valid():
                    return JsonResponse(response_serializer.data)
                else:
                    return JsonResponse({
                        'success': True,
                        'message': 'Service updated successfully',
                        'service': service_serializer.data
                    })
            else:
                error_response = {
                    'success': False,
                    'error': 'Validation failed',
                    'details': serializer.errors
                }
                return JsonResponse(error_response, status=400)
                
        except Service.DoesNotExist:
            error_response = {
                'success': False,
                'error': 'Service not found'
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
def service_list(request):
    """
    GET /api/services/ - returns JSON list of services
    """
    if request.method == 'GET':
        services = Service.objects.all().order_by('-created_at')
        serializer = ServiceSerializer(services, many=True)
        
        response_data = {
            'success': True,
            'count': services.count(),
            'services': serializer.data
        }
        
        response_serializer = ServiceListResponseSerializer(data=response_data)
        if response_serializer.is_valid():
            return JsonResponse(response_serializer.data)
        else:
            return JsonResponse(response_data)


@csrf_exempt
def create_service(request):
    """
    POST /api/services/create/ - creates a new service
    """
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
                
                # Prepare files data
                files = {}
                for key in request.FILES:
                    files[key] = request.FILES[key]
                
                # Combine data and files
                all_data = {}
                all_data.update(data)
                all_data.update(files)
                
                serializer = ServiceCreateSerializer(data=all_data)
            else:
                # Handle JSON data
                data = json.loads(request.body)
                serializer = ServiceCreateSerializer(data=data)
            
            if serializer.is_valid():
                service = serializer.save()
                service_serializer = ServiceSerializer(service)
                
                response_data = {
                    'success': True,
                    'message': 'Service created successfully',
                    'service': service_serializer.data
                }
                
                response_serializer = ServiceCreateResponseSerializer(data=response_data)
                if response_serializer.is_valid():
                    return JsonResponse(response_serializer.data, status=201)
                else:
                    return JsonResponse({
                        'success': True,
                        'message': 'Service created successfully',
                        'service': service_serializer.data
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


# Create your views here.


@csrf_exempt
def delete_service(request, pk):
    """
    POST /api/services/{id}/delete/ - deletes a service
    """
    if request.method == 'POST':
        try:
            service = Service.objects.get(pk=pk)
            service_name = service.name
            service.delete()
            
            response_data = {
                'success': True,
                'message': f'Service "{service_name}" deleted successfully'
            }
            return JsonResponse(response_data)
        except Service.DoesNotExist:
            response_data = {
                'success': False,
                'error': 'Service not found'
            }
            return JsonResponse(response_data, status=404)
        except Exception as e:
            response_data = {
                'success': False,
                'error': str(e)
            }
            return JsonResponse(response_data, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)