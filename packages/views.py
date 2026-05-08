from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Package
from .serializers import (
    PackageSerializer, PackageCreateSerializer,
    PackageListResponseSerializer, PackageCreateResponseSerializer, APIResponseSerializer
)
import json


@csrf_exempt
def package_list(request):
    """
    GET /api/packages/ - returns JSON list of packages
    """
    if request.method == 'GET':
        packages = Package.objects.all().order_by('-created_at')
        serializer = PackageSerializer(packages, many=True)
        
        response_data = {
            'success': True,
            'count': packages.count(),
            'packages': serializer.data
        }
        
        response_serializer = PackageListResponseSerializer(data=response_data)
        if response_serializer.is_valid():
            return JsonResponse(response_serializer.data)
        else:
            return JsonResponse(response_data)


@csrf_exempt
def create_package(request):
    """
    POST /api/packages/create/ - creates a new package
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            serializer = PackageCreateSerializer(data=data)
            
            if serializer.is_valid():
                package = serializer.save()
                package_serializer = PackageSerializer(package)
                
                response_data = {
                    'success': True,
                    'message': 'Package created successfully',
                    'package': package_serializer.data
                }
                
                response_serializer = PackageCreateResponseSerializer(data=response_data)
                if response_serializer.is_valid():
                    return JsonResponse(response_serializer.data, status=201)
                else:
                    return JsonResponse({
                        'success': True,
                        'message': 'Package created successfully',
                        'package': package_serializer.data
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
    Redirect to centralized GET API testing page for packages app
    """
    from django.shortcuts import redirect
    return redirect('/dashboard/api/testing/get/?app=packages')


def api_post_testing(request):
    """
    Redirect to centralized POST API testing page for packages app
    """
    from django.shortcuts import redirect
    return redirect('/dashboard/api/testing/post/?app=packages')


def package_list_html(request):
    """
    Render the package list HTML page
    """
    from .models import Package
    packages = Package.objects.all().order_by('-created_at')
    context = {
        'packages': packages,
        'app_name': 'packages',
        'model_name': 'Package',
        'current_page': 'packages'
    }
    return render(request, 'packages/list.html', context)


def package_add_html(request):
    """
    Render the package add HTML page
    """
    context = {
        'app_name': 'packages',
        'model_name': 'Package'
    }
    return render(request, 'packages/add.html', context)


def package_detail_html(request, pk):
    """
    Render the package detail HTML page
    """
    from .models import Package
    package = Package.objects.get(id=pk)
    context = {
        'package': package,
        'app_name': 'packages',
        'model_name': 'Package'
    }
    return render(request, 'packages/view.html', context)


def package_edit_html(request, pk):
    """
    Render the package edit HTML page
    """
    from .models import Package
    package = Package.objects.get(id=pk)
    context = {
        'package': package,
        'app_name': 'packages',
        'model_name': 'Package'
    }
    return render(request, 'packages/edit.html', context)


@csrf_exempt
def update_package(request, pk):
    """
    PUT /api/packages/{id}/update/ - updates an existing package
    """
    if request.method == 'PUT':
        try:
            package = Package.objects.get(pk=pk)
            data = json.loads(request.body)
            serializer = PackageCreateSerializer(package, data=data, partial=True)
            
            if serializer.is_valid():
                updated_package = serializer.save()
                package_serializer = PackageSerializer(updated_package)
                
                response_data = {
                    'success': True,
                    'message': 'Package updated successfully',
                    'package': package_serializer.data
                }
                
                response_serializer = PackageCreateResponseSerializer(data=response_data)
                if response_serializer.is_valid():
                    return JsonResponse(response_serializer.data)
                else:
                    return JsonResponse({
                        'success': True,
                        'message': 'Package updated successfully',
                        'package': package_serializer.data
                    })
            else:
                error_response = {
                    'success': False,
                    'error': 'Validation failed',
                    'details': serializer.errors
                }
                return JsonResponse(error_response, status=400)
                
        except Package.DoesNotExist:
            error_response = {
                'success': False,
                'error': 'Package not found'
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
def delete_package(request, pk):
    """
    POST /packages/<uuid:pk>/delete/ - deletes an existing package
    """
    if request.method == 'POST':
        try:
            package = Package.objects.get(pk=pk)
            package.delete()
            
            # Redirect back to the package list page after successful deletion
            from django.shortcuts import redirect
            return redirect('packages:package_list')
                
        except Package.DoesNotExist:
            # Even if package doesn't exist, redirect back to the list page
            from django.shortcuts import redirect
            return redirect('packages:package_list')
        except Exception as e:
            # On any error, redirect back to the list page
            from django.shortcuts import redirect
            return redirect('packages:package_list')
    
    # If not a POST request, redirect back to the list page
    from django.shortcuts import redirect
    return redirect('packages:package_list')