from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Product
from .serializers import (
    ProductSerializer, ProductCreateSerializer,
    ProductListResponseSerializer, ProductCreateResponseSerializer, APIResponseSerializer
)
import json


@csrf_exempt
def product_list(request):
    """
    GET /api/products/ - returns JSON list of products
    """
    if request.method == 'GET':
        products = Product.objects.all().order_by('-created_at')
        serializer = ProductSerializer(products, many=True)
        
        response_data = {
            'success': True,
            'count': products.count(),
            'products': serializer.data
        }
        
        response_serializer = ProductListResponseSerializer(data=response_data)
        if response_serializer.is_valid():
            return JsonResponse(response_serializer.data)
        else:
            return JsonResponse(response_data)


@csrf_exempt
def create_product(request):
    """
    POST /api/products/create/ - creates a new product
    Supports both JSON and form data (for file uploads)
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
                    
                # Convert numeric fields
                if 'price' in data:
                    try:
                        data['price'] = float(data['price'])
                    except ValueError:
                        data['price'] = None
                        
                if 'stock_quantity' in data:
                    try:
                        data['stock_quantity'] = int(data['stock_quantity'])
                    except ValueError:
                        data['stock_quantity'] = 0
                
                # Prepare files data
                files = {}
                for key in request.FILES:
                    files[key] = request.FILES[key]
                
                # Combine data and files
                all_data = {}
                all_data.update(data)
                all_data.update(files)
                
                serializer = ProductCreateSerializer(data=all_data)
            else:
                # Handle JSON data
                data = json.loads(request.body)
                serializer = ProductCreateSerializer(data=data)
            
            if serializer.is_valid():
                product = serializer.save()
                product_serializer = ProductSerializer(product)
                
                response_data = {
                    'success': True,
                    'message': 'Product created successfully',
                    'product': product_serializer.data
                }
                
                response_serializer = ProductCreateResponseSerializer(data=response_data)
                if response_serializer.is_valid():
                    return JsonResponse(response_serializer.data, status=201)
                else:
                    return JsonResponse({
                        'success': True,
                        'message': 'Product created successfully',
                        'product': product_serializer.data
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


def product_list_html(request):
    """
    Render the product list HTML page
    """
    from .models import Product
    products = Product.objects.all().order_by('-created_at')
    context = {
        'products': products,
        'app_name': 'products',
        'model_name': 'Product',
        'current_page': 'products'
    }
    return render(request, 'products/list.html', context)


def product_add_html(request):
    """
    Render the product add HTML page
    """
    context = {
        'app_name': 'products',
        'model_name': 'Product'
    }
    return render(request, 'products/add.html', context)


def product_detail_html(request):
    """
    Render the product detail HTML page
    """
    from .models import Product
    product_id = request.GET.get('id')
    
    if not product_id:
        # If no ID is provided, redirect to the product list
        from django.shortcuts import redirect
        return redirect('products:product_list')
    
    try:
        product = Product.objects.get(id=product_id)
        context = {
            'product': product,
            'app_name': 'products',
            'model_name': 'Product'
        }
        return render(request, 'products/view.html', context)
    except Product.DoesNotExist:
        # If product doesn't exist, redirect to the product list
        from django.shortcuts import redirect
        return redirect('products:product_list')


def product_edit_html(request, pk):
    """
    Render the product edit HTML page
    """
    from .models import Product
    product = Product.objects.get(id=pk)
    context = {
        'product': product,
        'app_name': 'products',
        'model_name': 'Product'
    }
    return render(request, 'products/edit.html', context)


@csrf_exempt
def update_product(request, pk):
    """
    PUT /api/products/{id}/update/ - updates an existing product
    Supports both JSON and form data (for file uploads)
    """
    if request.method == 'PUT':
        try:
            product = Product.objects.get(pk=pk)
            
            if request.content_type.startswith('multipart/form-data') or request.content_type.startswith('application/x-www-form-urlencoded'):
                # Handle form data (including file uploads)
                data = {}
                for key in request.POST:
                    data[key] = request.POST[key]
                
                # Convert boolean fields
                if 'is_active' in data:
                    data['is_active'] = data['is_active'] in ['true', '1', 'on', 'yes']
                    
                # Convert numeric fields
                if 'price' in data:
                    try:
                        data['price'] = float(data['price'])
                    except ValueError:
                        data['price'] = None
                        
                if 'stock_quantity' in data:
                    try:
                        data['stock_quantity'] = int(data['stock_quantity'])
                    except ValueError:
                        data['stock_quantity'] = 0
                
                # Prepare files data
                files = {}
                for key in request.FILES:
                    files[key] = request.FILES[key]
                
                # Combine data and files
                all_data = {}
                all_data.update(data)
                all_data.update(files)
                
                serializer = ProductCreateSerializer(product, data=all_data, partial=True)
            else:
                # Handle JSON data
                data = json.loads(request.body)
                serializer = ProductCreateSerializer(product, data=data, partial=True)
            
            if serializer.is_valid():
                updated_product = serializer.save()
                product_serializer = ProductSerializer(updated_product)
                
                response_data = {
                    'success': True,
                    'message': 'Product updated successfully',
                    'product': product_serializer.data
                }
                
                response_serializer = ProductCreateResponseSerializer(data=response_data)
                if response_serializer.is_valid():
                    return JsonResponse(response_serializer.data)
                else:
                    return JsonResponse({
                        'success': True,
                        'message': 'Product updated successfully',
                        'product': product_serializer.data
                    })
            else:
                error_response = {
                    'success': False,
                    'error': 'Validation failed',
                    'details': serializer.errors
                }
                return JsonResponse(error_response, status=400)
                
        except Product.DoesNotExist:
            error_response = {
                'success': False,
                'error': 'Product not found'
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
def delete_product(request, pk):
    """
    POST /products/<uuid:pk>/delete/ - deletes an existing product
    """
    if request.method == 'POST':
        try:
            product = Product.objects.get(pk=pk)
            product.delete()
            
            # Redirect back to the product list page after successful deletion
            from django.shortcuts import redirect
            return redirect('products:product_list')
                
        except Product.DoesNotExist:
            # Even if product doesn't exist, redirect back to the list page
            from django.shortcuts import redirect
            return redirect('products:product_list')
        except Exception as e:
            # On any error, redirect back to the list page
            from django.shortcuts import redirect
            return redirect('products:product_list')
    
    # If not a POST request, redirect back to the list page
    from django.shortcuts import redirect
    return redirect('products:product_list')