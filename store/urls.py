# store/urls.py (For the customer-facing shop)

from django.urls import path
from . import views 

# This is the application namespace name. 
# It must match the namespace defined in my_ecommerce_site/urls.py
app_name = 'store' 

urlpatterns = [
    # Defines the URL name 'store:store'
    path('', views.store_view, name='store'), 
    
    # Defines the URL name 'store:product_detail'
    path('product/<int:pk>/', views.product_detail_view, name='product_detail'), 
    
    # Defines the URL name 'store:cart'
    path('cart/', views.cart_view, name='cart'), 
    
    # Defines the URL name 'store:orders'
    path('orders/', views.orders_view, name='orders'),
    
    # Defines the URL name 'store:checkout'
    path('checkout/', views.checkout_view, name='checkout'), 
    
    # Defines the URL name 'store:update_item' (for AJAX)
    path('update_item/', views.update_item, name='update_item'), 
    
    # Defines the URL name 'store:process_order' (for AJAX)
    path('process_order/', views.process_order, name='process_order'), 
    
    # Policy Pages
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    path('terms-conditions/', views.terms_conditions_view, name='terms_conditions'),
    path('shipping-info/', views.shipping_info_view, name='shipping_info'),
    path('about-us/', views.about_us_view, name='about_us'),
    # Analytics recording endpoint (AJAX)
    path('analytics/record/', views.record_page_view, name='record_page_view'),
    # Ensure session endpoint (call from client to force session creation)
    path('session/ensure/', views.ensure_session, name='ensure_session'),
    # Shipping estimate (TomTom-backed) for towns not in static list
    path('shipping/estimate/', views.shipping_estimate, name='shipping_estimate'),
    # Temporary debug endpoint to inspect live site visit counts
    path('analytics/debug/site_visits/', views.debug_site_visits, name='debug_site_visits'),
    # Temporary admin-only endpoint to run migrations remotely (use with caution)
    path('run-migrations/', views.run_migrations, name='run_migrations'),
]