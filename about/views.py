
from django.shortcuts import render
from .models import About

def about_view(request):
    # .first() gets the first (and usually only) entry in the About table
    about_data = About.objects.first() 
    return render(request, 'about/about.html', {'about': about_data})