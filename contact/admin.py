from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils.html import format_html
import urllib.parse
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    # This makes the admin list look like an actual inbox
    list_display = ('name', 'subject', 'created_at', 'is_read', 'reply_link')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')

    def reply_link(self, obj):
        # Professional Email Template
        body = f"Hello {obj.name},\n\nThank you for reaching out to us regarding '{obj.subject}'.\n\n[Write your message here]\n\nBest regards,\nYour Store Team"
        
        # Encode for URL
        params = urllib.parse.urlencode({
            'to': obj.email,
            'subject': f"Re: {obj.subject}",
            'body': body
        })
        
        gmail_url = f"https://mail.google.com/mail/?view=cm&fs=1&{params}"
        
        return format_html(
            '<a class="button" href="{}" target="_blank" style="background-color: #f4cca4; color: #1c1427; font-weight:bold;">Reply via Gmail</a>', gmail_url
        )

    reply_link.short_description = "Action"