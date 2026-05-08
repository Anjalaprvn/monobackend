from django.shortcuts import render

def home(request):
    """
    Render the base homepage template
    """
    return render(request, 'home.html')