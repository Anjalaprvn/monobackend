from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Client
from .serializers import (
    ClientSerializer, ClientCreateSerializer,
    ClientListResponseSerializer, ClientCreateResponseSerializer, APIResponseSerializer
)
import json


@csrf_exempt
def client_list(request):
    """
    GET /api/clients/ - returns JSON list of clients
    """
    if request.method == 'GET':
        clients = Client.objects.all().order_by('-created_at')
        serializer = ClientSerializer(clients, many=True)
        
        response_data = {
            'success': True,
            'count': clients.count(),
            'clients': serializer.data
        }
        
        response_serializer = ClientListResponseSerializer(data=response_data)
        if response_serializer.is_valid():
            return JsonResponse(response_serializer.data)
        else:
            return JsonResponse(response_data)


@csrf_exempt
def create_client(request):
    """
    POST /api/clients/create/ - creates a new client
    
    Expected JSON payload:
    {
        "name": "Client Name",
        "website": "https://example.com",
        "logo": "base64_encoded_image_data",  // Optional
        "is_active": true  // Optional, defaults to true
    }
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Handle logo field mapping
            if 'logo' in data and data['logo']:
                # If logo is provided as base64 string, handle it
                # For now, we'll just pass it through - you may want to process base64 images
                pass
            elif 'logo' in data:
                # If logo is null/empty, remove it from data
                data.pop('logo', None)
            
            serializer = ClientCreateSerializer(data=data)
            
            if serializer.is_valid():
                client = serializer.save()
                client_serializer = ClientSerializer(client)
                
                response_data = {
                    'success': True,
                    'message': 'Client created successfully',
                    'client': client_serializer.data
                }
                
                response_serializer = ClientCreateResponseSerializer(data=response_data)
                if response_serializer.is_valid():
                    return JsonResponse(response_serializer.data, status=201)
                else:
                    return JsonResponse({
                        'success': True,
                        'message': 'Client created successfully',
                        'client': client_serializer.data
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
    Redirect to centralized GET API testing page for clients app
    """
    from django.shortcuts import redirect
    return redirect('/dashboard/api/testing/get/?app=clients')


def api_post_testing(request):
    """
    Redirect to centralized POST API testing page for clients app
    """
    from django.shortcuts import redirect
    return redirect('/dashboard/api/testing/post/?app=clients')


def client_list_html(request):
    """
    Render the client list HTML page
    """
    from .models import Client
    clients = Client.objects.all().order_by('-created_at')
    context = {
        'clients': clients,
        'app_name': 'clients',
        'model_name': 'Client',
        'current_page': 'clients'
    }
    return render(request, 'clients/list.html', context)


def client_add_html(request):
    """
    Render the client add HTML page
    """
    context = {
        'app_name': 'clients',
        'model_name': 'Client'
    }
    return render(request, 'clients/add.html', context)


def client_detail_html(request, pk=None):
    """
    Render the client detail HTML page
    """
    from .models import Client
    if pk:
        try:
            client = Client.objects.get(id=pk)
        except Client.DoesNotExist:
            from django.shortcuts import redirect
            return redirect('clients:client_list')
    else:
        # If no ID is provided, redirect to client list
        from django.shortcuts import redirect
        return redirect('clients:client_list')
    
    context = {
        'client': client,
        'app_name': 'clients',
        'model_name': 'Client'
    }
    return render(request, 'clients/view.html', context)


def client_edit_html(request, pk=None):
    """
    Render the client edit HTML page
    """
    from .models import Client
    if pk:
        try:
            client = Client.objects.get(id=pk)
        except Client.DoesNotExist:
            from django.shortcuts import redirect
            return redirect('clients:client_list')
    else:
        # If no ID is provided, redirect to client list
        from django.shortcuts import redirect
        return redirect('clients:client_list')
    
    context = {
        'client': client,
        'app_name': 'clients',
        'model_name': 'Client'
    }
    return render(request, 'clients/edit.html', context)


@csrf_exempt
def update_client(request):
    """
    PUT /api/clients/update/ - updates an existing client using query parameter
    Supports both JSON and form data (for file uploads)
    """
    if request.method == 'PUT':
        try:
            client_id = request.GET.get('id')
            if not client_id:
                error_response = {
                    'success': False,
                    'error': 'Client ID is required'
                }
                return JsonResponse(error_response, status=400)
            
            client = Client.objects.get(pk=client_id)
            data = json.loads(request.body)
            serializer = ClientCreateSerializer(client, data=data, partial=True)
            
            if serializer.is_valid():
                updated_client = serializer.save()
                client_serializer = ClientSerializer(updated_client)
                
                response_data = {
                    'success': True,
                    'message': 'Client updated successfully',
                    'client': client_serializer.data
                }
                
                response_serializer = ClientCreateResponseSerializer(data=response_data)
                if response_serializer.is_valid():
                    return JsonResponse(response_serializer.data)
                else:
                    return JsonResponse({
                        'success': True,
                        'message': 'Client updated successfully',
                        'client': client_serializer.data
                    })
            else:
                error_response = {
                    'success': False,
                    'error': 'Validation failed',
                    'details': serializer.errors
                }
                return JsonResponse(error_response, status=400)
                
        except Client.DoesNotExist:
            error_response = {
                'success': False,
                'error': 'Client not found'
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
def delete_client(request, pk):
    """
    POST /clients/<uuid:pk>/delete/ - deletes an existing client
    """
    if request.method == 'POST':
        try:
            client = Client.objects.get(pk=pk)
            client.delete()
            
            # Redirect back to the client list page after successful deletion
            from django.shortcuts import redirect
            return redirect('clients:client_list')
                
        except Client.DoesNotExist:
            # Even if client doesn't exist, redirect back to the list page
            from django.shortcuts import redirect
            return redirect('clients:client_list')
        except Exception as e:
            # On any error, redirect back to the list page
            from django.shortcuts import redirect
            return redirect('clients:client_list')
    
    # If not a POST request, redirect back to the list page
    from django.shortcuts import redirect
    return redirect('clients:client_list')