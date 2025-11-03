# my_ecommerce_site/urls.py (CORRECTED)

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from allauth.account.views import LoginView
from store import views as store_views 
from services import views as services_views 

# --- New pattern list for the Portal, using a dedicated namespace ---
portal_urlpatterns = [
    # General Portal Paths (Inventory Dashboard, Service Requests List, Login)
    path('login/', LoginView.as_view(template_name='account/login_portal.html'), name='login'), 
    path('dashboard/inventory/', store_views.inventory_dashboard, name='inventory_dashboard'),
    path('service_requests/', services_views.staff_requests_list, name="staff_requests_list"),
    
    # Product Management Paths
    path('products/add/', store_views.add_product, name='add_product'), 
    path('products/edit/<int:pk>/', store_views.edit_product, name='edit_product'),
    path('products/delete/<int:pk>/', store_views.delete_product, name='delete_product'),
    
    # NEW: Log Activity Page Path
    path('log/all/', store_views.all_activity_log_view, name='all_activity_log'),

    # Add Staff Chat URL to the portal namespace
    path('service_requests/chat/<int:pk>/', services_views.staff_service_request_chat, name='staff_chat'),
]
# --------------------------------------------------------------------

urlpatterns = [
    # NEW ROOT PATH FOR HOME PAGE
    path('', store_views.home_view, name='home'), 
    
    # USER-FACING AUTHENTICATION (ALLAUTH HANDLES THIS)
    path('accounts/', include('allauth.urls')), 
    
    path('admin/', admin.site.urls),

    # ------------------------------------
    # --- CONSOLIDATED APP PATHS (Customer Shop) ---
    # ------------------------------------
    # All customer-facing store paths are now under /store/ and use the 'store:' namespace
    path('store/', include(('store.urls', 'store'), namespace='store')), 
    path('services/', include('services.urls')), 
    
    # ------------------------------------
    # --- GLOBAL PORTAL / ADMIN PATHS (using the 'portal' namespace) ---
    # ------------------------------------
    path('portal/', include((portal_urlpatterns, 'portal'), namespace='portal')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
