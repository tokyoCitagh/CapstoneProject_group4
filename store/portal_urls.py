from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- PUBLIC STOREFRONT URLS ---
    path('store/', include('store.urls')), 
    
    # --- ACCOUNT/AUTH URLS (Used by allauth) ---
    path('accounts/', include('allauth.urls')), 
    
    # --- STAFF PORTAL URLS (CRITICAL FIX: Ensure 'portal' namespace is used) ---
    path('portal/', include('store.portal_urls')), # Assuming the new file is 'store/portal_urls.py'
    
    # --- SERVICES URLS (If not already included in portal) ---
    # path('services/', include('services.urls')), # Uncomment if services has its own namespace
    
    # Catch-all or Home
    path('', include('store.urls')), # Or point to a dedicated home view
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)