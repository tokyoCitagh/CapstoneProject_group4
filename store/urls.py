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
    
    # Defines the URL name 'store:checkout'
    path('checkout/', views.checkout_view, name='checkout'), 
    
    # Defines the URL name 'store:update_item' (for AJAX)
    path('update_item/', views.update_item, name='update_item'), 
    
    # Defines the URL name 'store:process_order' (for AJAX)
    path('process_order/', views.process_order, name='process_order'), 
]