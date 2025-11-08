# my_ecommerce_site/urls.py (FINAL FIX)

from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView 
from store import views as store_views 
from services import views as services_views 

# CRITICAL SETTINGS FOR LOGIN VIEW
STAFF_LOGOUT_URL = reverse_lazy('portal:login')


# --- New pattern list for the Portal, using a dedicated namespace ---
portal_urlpatterns = [
    # STAFF LOGIN PATH DEFINED HERE
    path('login/', 
         store_views.portal_login_view, 
         name='login'), # This name will now be accessed as 'portal:login'
    
    path('dashboard/inventory/', store_views.inventory_dashboard, name='inventory_dashboard'),
    path('service_requests/', services_views.staff_requests_list, name="staff_requests_list"),
    
    # ... other portal views ...
    path('products/', 
         RedirectView.as_view(pattern_name='portal:inventory_dashboard', permanent=False), 
         name='product_index_redirect'),
         
    path('products/add/', store_views.add_product, name='add_product'), 
    path('products/edit/<int:pk>/', store_views.edit_product, name='edit_product'),
    path('products/delete/<int:pk>/', store_views.delete_product, name='delete_product'),
    path('log/all/', store_views.all_activity_log_view, name='all_activity_log'),
    path('service_requests/chat/<int:pk>/', services_views.staff_service_request_chat, name='staff_chat'),

    # STAFF LOGOUT PATH 
    path('logout/', 
         DjangoLogoutView.as_view(next_page=STAFF_LOGOUT_URL), 
         name='logout'),
]
# --------------------------------------------------------------------

urlpatterns = [
    # ROOT PATH
    path('', store_views.home_view, name='home'), 
    
    # Authentication URLs
    path('accounts/', include('allauth.urls')),
    
    # Custom email page override
    path('accounts/email/', store_views.custom_email_list_view, name='account_email'),
    
    # ALLAUTH PATHS (NOW HANDLES ALL LOGIN, LOGOUT, AND PASSWORD RESET)
    path('accounts/', include('allauth.urls')), 
    
    path('admin/', admin.site.urls),

    # CUSTOMER SHOP PATHS
    path('store/', include(('store.urls', 'store'), namespace='store')), 
    path('services/', include('services.urls')), 
    
    # STAFF PORTAL PATHS (Namespaced)
    path('portal/', include((portal_urlpatterns, 'portal'), namespace='portal')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)