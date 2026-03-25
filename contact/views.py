from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm
from django.http import JsonResponse

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
          # This adds a message that Django will show after the reload
            messages.success(request, "Your message has been sent! We will get back to you soon.")
            return redirect('contact:contact_page')
    else:
        form = ContactForm()
    
    return render(request, 'contact/contact.html', {'form': form})