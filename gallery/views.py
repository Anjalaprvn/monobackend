from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Gallery, GalleryImage
from .serializers import (
    GallerySerializer, GalleryCreateSerializer,
    GalleryListResponseSerializer, GalleryCreateResponseSerializer, APIResponseSerializer
)
import json
from django.shortcuts import get_object_or_404


@csrf_exempt
def gallery_list(request):
    """
    GET /api/gallery/ - returns JSON list of gallery items
    """
    if request.method == 'GET':
        galleries = Gallery.objects.all().order_by('-created_at')
        serializer = GallerySerializer(galleries, many=True)
        
        response_data = {
            'success': True,
            'count': galleries.count(),
            'galleries': serializer.data
        }
        
        response_serializer = GalleryListResponseSerializer(data=response_data)
        if response_serializer.is_valid():
            return JsonResponse(response_serializer.data)
        else:
            return JsonResponse(response_data)


@csrf_exempt
def create_gallery_item(request):
    """
    POST /api/gallery/create/ - creates a new gallery item with multiple images
    """
    if request.method == 'POST':
        try:
            if request.content_type.startswith('multipart/form-data') or request.content_type.startswith('application/x-www-form-urlencoded'):
                data = {}

                for key in request.POST:
                    data[key] = request.POST[key]

                if 'is_active' in data:
                    data['is_active'] = data['is_active'] in ['true', '1', 'on', 'yes']

                images = []
                if 'images' in request.FILES:
                    images = request.FILES.getlist('images')

                all_data = {**data}
                if images:
                    all_data['images'] = images

                serializer = GalleryCreateSerializer(data=all_data)

            else:
                data = json.loads(request.body)
                serializer = GalleryCreateSerializer(data=data)

            if serializer.is_valid():
                gallery = serializer.save()  # ✅ images handled INSIDE serializer

                gallery_serializer = GallerySerializer(gallery)

                return JsonResponse({
                    'success': True,
                    'message': 'Gallery item created successfully',
                    'gallery': gallery_serializer.data
                }, status=201)

            return JsonResponse({
                'success': False,
                'error': 'Validation failed',
                'details': serializer.errors
            }, status=400)

        except Exception as e:
            import traceback
            return JsonResponse({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)




def gallery_list_html(request):
    """
    Render the gallery list HTML page
    """
    items = Gallery.objects.all().order_by('-created_at')
    context = {
        'items': items,
        'app_name': 'gallery',
        'model_name': 'Gallery Item',
        'current_page': 'gallery'
    }
    return render(request, 'gallery/list.html', context)


def gallery_add_html(request):
    """
    Render the gallery add HTML page
    """
    context = {
        'app_name': 'gallery',
        'model_name': 'Gallery Item'
    }
    return render(request, 'gallery/add.html', context)


def gallery_detail_html(request, pk):
    """
    Render the gallery detail HTML page for a specific item
    """
    item = get_object_or_404(Gallery, id=pk)
    context = {
        'item': item,
        'app_name': 'gallery',
        'model_name': 'Gallery Item'
    }
    return render(request, 'gallery/view.html', context)


def gallery_latest_detail_html(request):
    """
    Render the gallery detail HTML page for the latest item
    """
    # Get the most recently created gallery item
    item = Gallery.objects.order_by('-created_at').first()
    if not item:
        # If no items exist, redirect to gallery list
        from django.shortcuts import redirect
        return redirect('gallery:gallery_list')
    
    context = {
        'item': item,
        'app_name': 'gallery',
        'model_name': 'Gallery Item'
    }
    return render(request, 'gallery/view.html', context)


def gallery_edit_html(request, pk):
    """
    Render the gallery edit HTML page
    """
    item = get_object_or_404(Gallery, id=pk)
    context = {
        'item': item,
        'app_name': 'gallery',
        'model_name': 'Gallery Item'
    }
    return render(request, 'gallery/edit.html', context)


@csrf_exempt
def delete_gallery_item(request, pk):
    """
    POST /gallery/<uuid:pk>/delete/ - deletes an existing gallery item
    """
    if request.method == 'POST':
        try:
            item = Gallery.objects.get(pk=pk)
            item.delete()
            
            # Redirect back to the gallery list page after successful deletion
            from django.shortcuts import redirect
            return redirect('gallery:gallery_list')
                
        except Gallery.DoesNotExist:
            # Even if item doesn't exist, redirect back to the list page
            from django.shortcuts import redirect
            return redirect('gallery:gallery_list')
        except Exception as e:
            # On any error, redirect back to the list page
            from django.shortcuts import redirect
            return redirect('gallery:gallery_list')
    
    # If not a POST request, redirect back to the list page
    from django.shortcuts import redirect
    return redirect('gallery:gallery_list')


@csrf_exempt
def update_gallery_item(request, pk):
    """
    PUT /api/gallery/{id}/update/ - updates an existing gallery item
    Supports both JSON and form data (for file uploads)
    """
    if request.method == 'PUT':
        try:
            gallery = Gallery.objects.get(pk=pk)
            if request.content_type.startswith('multipart/form-data') or request.content_type.startswith('application/x-www-form-urlencoded'):
                # Handle form data (including file uploads)
                data = {}
                for key in request.POST:
                    data[key] = request.POST[key]
                
                # Convert boolean fields
                if 'is_active' in data:
                    data['is_active'] = data['is_active'] in ['true', '1', 'on', 'yes']
                
                # Handle multiple images
                images = []
                for key in request.FILES:
                    if key == 'images':
                        # Handle multiple files
                        images.extend([request.FILES[key] for key in request.FILES.getlist('images')])
                    else:
                        # Handle single files (backward compatibility)
                        images.append(request.FILES[key])
                
                # Combine data and files
                all_data = {}
                all_data.update(data)
                if images:
                    all_data['images'] = images
                
                serializer = GalleryCreateSerializer(gallery, data=all_data, partial=True)
            else:
                # Handle JSON data
                data = json.loads(request.body)
                serializer = GalleryCreateSerializer(gallery, data=data, partial=True)
            
            if serializer.is_valid():
                # Handle image files separately before saving the gallery
                images = []
                if request.FILES.getlist('images'):
                    images = request.FILES.getlist('images')
                elif request.FILES.get('images'):
                    images = [request.FILES.get('images')]
                
                updated_gallery = serializer.save()
                
                # Handle new image files if provided
                for i, image_file in enumerate(images):
                    GalleryImage.objects.create(
                        gallery=updated_gallery,
                        image=image_file,
                        is_primary=(i == 0 and not updated_gallery.images.exists())
                    )
                
                gallery_serializer = GallerySerializer(updated_gallery)
                
                response_data = {
                    'success': True,
                    'message': 'Gallery item updated successfully',
                    'gallery': gallery_serializer.data
                }
                
                response_serializer = GalleryCreateResponseSerializer(data=response_data)
                if response_serializer.is_valid():
                    return JsonResponse(response_serializer.data)
                else:
                    return JsonResponse({
                        'success': True,
                        'message': 'Gallery item updated successfully',
                        'gallery': gallery_serializer.data
                    })
            else:
                error_response = {
                    'success': False,
                    'error': 'Validation failed',
                    'details': serializer.errors
                }
                return JsonResponse(error_response, status=400)
                
        except Gallery.DoesNotExist:
            error_response = {
                'success': False,
                'error': 'Gallery item not found'
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