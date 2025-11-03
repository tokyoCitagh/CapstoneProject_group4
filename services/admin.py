# services/admin.py (UPDATED)

from django.contrib import admin
from django.utils.html import format_html # Needed to render HTML links
from django.urls import reverse # Needed to generate URLs by name
from .models import ServiceRequest, QuoteMessage

# 1. Define ServiceRequestAdmin class
class ServiceRequestAdmin(admin.ModelAdmin):
    # ADDED 'chat_link' to the list_display
    list_display = ('id', 'customer', 'service_type', 'status', 'date_requested', 'chat_link') 
    list_filter = ('status', 'service_type')
    search_fields = ('customer__name', 'description')

    # NEW METHOD: Generates a clickable link to the custom chat view
    def chat_link(self, obj):
        # 'service_request_chat' is the name defined in services/urls.py
        url = reverse('service_request_chat', args=[obj.pk]) 
        
        # Use format_html to render the anchor tag
        return format_html('<a href="{}">Open Chat</a>', url)
        
    chat_link.short_description = 'Chat' # Column header name

# 2. Define QuoteMessageAdmin class (No change needed)
class QuoteMessageAdmin(admin.ModelAdmin):
    list_display = ('request', 'sender', 'timestamp', 'message_preview') 
    list_filter = ('sender',)

    def message_preview(self, obj):
        return obj.message[:50] + '...'
    message_preview.short_description = 'Message'

# 3. Register Models (No change needed)
admin.site.register(ServiceRequest, ServiceRequestAdmin)
admin.site.register(QuoteMessage, QuoteMessageAdmin)