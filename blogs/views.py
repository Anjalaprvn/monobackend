from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.text import slugify
from .models import Blog
from .serializers import (
    BlogSerializer, BlogCreateSerializer,
    BlogListResponseSerializer, BlogDetailResponseSerializer,
    BlogCreateResponseSerializer, APIResponseSerializer
)
import json


@csrf_exempt
def blog_list(request):
    """
    GET /api/blogs/ - returns JSON list of blogs
    GET /blogs/ - returns HTML page
    POST /api/blogs/ - Method not allowed
    """
    if request.method == 'GET':
        # Check if this is an API request
        if 'api' in request.path or request.headers.get('Accept') == 'application/json':
            blogs = Blog.objects.all().order_by('-created_at')
            serializer = BlogSerializer(blogs, many=True)
            
            # Create response data
            response_data = {
                'success': True,
                'count': blogs.count(),
                'blogs': serializer.data
            }
            
            # Validate with response serializer
            response_serializer = BlogListResponseSerializer(data=response_data)
            if response_serializer.is_valid():
                return JsonResponse(response_serializer.data)
            else:
                return JsonResponse(response_data)
        else:
            # Return HTML page for browser requests
            blogs = Blog.objects.all().order_by('-created_at')
            context = {
                'posts': blogs,  # Using 'posts' to match existing template
                'app_name': 'blogs',
                'model_name': 'Blog Posts',
                'current_page': 'blog'
            }
            return render(request, 'blogs/list.html', context)
    else:
        # Method not allowed for POST, PUT, DELETE, etc.
        return JsonResponse({
            'success': False,
            'error': 'Method not allowed. Use GET to retrieve blog list.'
        }, status=405)


@csrf_exempt
def blog_detail(request, slug):
    """
    GET /api/blogs/{slug}/ - returns JSON detail of specific blog
    GET /blogs/{slug}/ - returns HTML page
    POST /api/blogs/{slug}/ - Method not allowed
    """
    blog = get_object_or_404(Blog, slug=slug)
    
    if request.method == 'GET':
        # Check if this is an API request
        if 'api' in request.path or request.headers.get('Accept') == 'application/json':
            serializer = BlogSerializer(blog)
            
            # Create response data
            response_data = {
                'success': True,
                'blog': serializer.data
            }
            
            # Validate with response serializer
            response_serializer = BlogDetailResponseSerializer(data=response_data)
            if response_serializer.is_valid():
                return JsonResponse(response_serializer.data)
            else:
                return JsonResponse(response_data)
        else:
            # Return HTML page for browser requests
            context = {
                'blog': blog
            }
            return render(request, 'blogs/view.html', context)
    else:
        # Method not allowed for POST, PUT, DELETE, etc.
        return JsonResponse({
            'success': False,
            'error': 'Method not allowed. Use GET to retrieve blog details.'
        }, status=405)


@csrf_exempt
def create_blog(request):
    """
    POST /api/blogs/create/ - creates a new blog post
    """
    if request.method == 'POST':
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
                if request.FILES.get('cover_image'):
                    data['cover_image'] = request.FILES['cover_image']
            
            # Serialize and validate the data
            serializer = BlogCreateSerializer(data=data)
            
            if serializer.is_valid():
                # Save the blog post
                blog = serializer.save()
                
                # Serialize the created blog
                blog_serializer = BlogSerializer(blog)
                
                # Create success response
                response_data = {
                    'success': True,
                    'message': 'Blog post created successfully',
                    'blog': blog_serializer.data
                }
                
                response_serializer = BlogCreateResponseSerializer(data=response_data)
                if response_serializer.is_valid():
                    return JsonResponse(response_serializer.data, status=201)
                else:
                    return JsonResponse({
                        'success': True,
                        'message': 'Blog post created successfully',
                        'blog': blog_serializer.data
                    }, status=201)
            else:
                # Validation failed - print errors for debugging
                print("Validation errors:", serializer.errors)
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
                return JsonResponse(error_serializer.data, status=400)
            else:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=400)
    
    return JsonResponse({
        'error': 'Method not allowed'
    }, status=405)


@csrf_exempt
def delete_blog(request, blog_id):
    """
    Deletes a blog post. Accepts POST (from button) or DELETE (API) requests.
    """
    if request.method in ['POST', 'DELETE']:
        try:
            blog = Blog.objects.get(id=blog_id)
            blog_title = blog.title
            blog.delete()
            return JsonResponse({'success': True, 'message': f'Blog "{blog_title}" deleted successfully'})
        except Blog.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Blog post not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


def blog_add(request):
    """
    View to display the add blog post form
    """
    return render(request, 'blogs/add.html')

def blog_edit(request, blog_id):
    """
    Edit blog post (HTML only, no API)
    """
    blog = get_object_or_404(Blog, id=blog_id)

    if request.method == 'POST':
        blog.title = request.POST.get('title')
        blog.short_description = request.POST.get('short_description')
        blog.content = request.POST.get('content')
        blog.status = request.POST.get('status')
        blog.seo_title = request.POST.get('seo_title')
        blog.seo_description = request.POST.get('seo_description')

        # Update cover image if uploaded
        if request.FILES.get('cover_image'):
            blog.cover_image = request.FILES['cover_image']

        # Update slug if title changed
        new_title = request.POST.get('title')
        if new_title and new_title != blog.title:
            blog.slug = slugify(new_title)

        blog.save()

        return redirect('blogs:blog_list')

    return render(request, 'blogs/edit.html', {
        'blog': blog,
        'current_page': 'blog'
    })



def api_links(request):
    """
    View to display API testing links
    """
    api_endpoints = [
        {
            'name': 'Get All Blogs',
            'method': 'GET',
            'url': '/blogs/api/blogs/',
            'description': 'Returns list of all blog posts'
        },
        {
            'name': 'Create New Blog',
            'method': 'POST',
            'url': '/blogs/api/blogs/create/',
            'description': 'Creates a new blog post'
        },
        {
            'name': 'Get Blog Detail',
            'method': 'GET',
            'url': '/blogs/api/blogs/{slug}/',
            'description': 'Returns details of a specific blog post'
        },
        {
            'name': 'Delete Blog',
            'method': 'DELETE',
            'url': '/blogs/api/blogs/delete/{id}/',
            'description': 'Deletes a specific blog post'
        }
    ]
    
    context = {
        'api_endpoints': api_endpoints
    }
    return render(request, 'blogs/api_links.html', context)


def api_create_form(request):
    """
    View to display the API form for creating blog posts
    """
    return render(request, 'blogs/api_create_form.html')


def api_postman(request):
    """
    View to display Postman-style API testing interface
    """
    return render(request, 'blogs/api_postman.html')


# Create your views here.
