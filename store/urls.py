from django.urls import path
from . import views

app_name = 'store' 

urlpatterns = [
    # --- ONLY USER-FACING STOREFRONT PATHS REMAIN ---
    # Resolves to: /store/
    path('', views.store_view, name='store'), 
    # Resolves to: /store/product/1/
    path('product/<int:pk>/', views.product_detail_view, name='product_detail'), 
    # Resolves to: /store/cart/
    path('cart/', views.cart_view, name='cart'),
    # Resolves to: /store/checkout/
    path('checkout/', views.checkout_view, name='checkout'),
    
    # AJAX paths:
    path('update_item/', views.update_item, name='update_item'), 
    path('process_order/', views.process_order, name='process_order'),
    
    # --- PORTAL PATHS REMOVED ---
    # inventory_dashboard, add_product, edit_product, delete_product 
    # are now defined exclusively in my_ecommerce_site/urls.py under the /portal/ prefix.
]
