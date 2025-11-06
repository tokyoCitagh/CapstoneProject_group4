# my_ecommerce_site/urls.py

from django.contrib import admin
from django.urls import path, include, reverse_lazy
# Use the Django built-in LogoutView for reliable 'next_page' argument
from django.contrib.auth.views import LogoutView as DjangoLogoutView 
from allauth.account.views import LoginView
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView # <--- NEW IMPORT
from store import views as store_views 
from services import views as services_views 

# --- New pattern list for the Portal, using a dedicated namespace ---
portal_urlpatterns = [
    path('dashboard/inventory/', store_views.inventory_dashboard, name='inventory_dashboard'),
    path('service_requests/', services_views.staff_requests_list, name="staff_requests_list"),
    
    # **FIX: ADDED REDIRECT PATH** to handle the generic /portal/products/ URL
    path('products/', 
         RedirectView.as_view(pattern_name='portal:inventory_dashboard', permanent=False), 
         name='product_index_redirect'),
         
    # Product Management Paths
    path('products/add/', store_views.add_product, name='add_product'), 
    path('products/edit/<int:pk>/', store_views.edit_product, name='edit_product'),
    path('products/delete/<int:pk>/', store_views.delete_product, name='delete_product'),
    
    # Log Activity Page Path
    path('log/all/', store_views.all_activity_log_view, name='all_activity_log'),

    # Staff Chat URL to the portal namespace
    path('service_requests/chat/<int:pk>/', services_views.staff_service_request_chat, name='staff_chat'),

    # STAFF LOGOUT PATH
    path('logout/', 
         DjangoLogoutView.as_view(next_page=reverse_lazy('portal:login')), 
         name='logout'),
]
# --------------------------------------------------------------------

urlpatterns = [
    # ROOT PATH
    path('', store_views.home_view, name='home'), 
    
    # STAFF LOGIN PATH: Named 'login' for consistency with PORTAL_LOGIN_URL.
    path('portal/login/', 
         LoginView.as_view(
             template_name='account/login_portal.html',
             success_url=reverse_lazy('portal:inventory_dashboard')
         ), 
         name='login'),
    
    # ALLAUTH PATHS (Handles customer login/logout)
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