# store/views.py (FINAL UPDATED - Secure Portal Views)
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum 
from django.db import models # CRITICAL: Import models from 'django.db' to fix ImportError and use models.Q
from django.http import JsonResponse
from django.forms import inlineformset_factory 
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse, reverse_lazy
from django.utils import timezone 
from django.contrib import messages 
import json 

# --- CRITICAL IMPORTS ---
from .models import Product, Order, OrderItem, ProductImage, Customer, ShippingAddress, ActivityLog 
from .utils import cartData 
from services.models import ServiceRequest 
from .forms import ProductForm 
# -------------------------------------------------------------------------------------

# Define the Image Formset
ImageFormSet = inlineformset_factory(
    Product, 
    ProductImage, 
    fields=('image',), 
    extra=1, 
    can_delete=True
)

# --- UTILITY FUNCTION ---
def get_customer_or_create(request):
    """Utility function to safely get or create a Customer profile for an authenticated user."""
    customer = None
    if request.user.is_authenticated:
        try:
            customer = request.user.customer
        except Customer.DoesNotExist:
            customer = Customer.objects.create(
                user=request.user,
                name=request.user.username,
                email=request.user.email
            )
    return customer


# --- NEW: STAFF CHECK UTILITY FUNCTION ---
def is_staff_user(user):
    """Checks if the user is active and has staff privileges."""
    return user.is_active and user.is_staff

# Use reverse_lazy for decorators to resolve the URL name after settings are loaded
PORTAL_LOGIN_URL = reverse_lazy('portal:login') 

# --- USER-FACING E-COMMERCE VIEWS (NO CHANGES) ---

def home_view(request):
    """The main landing page for the site."""
    data = cartData(request) 
    context = {'cartItems': data['cartItems']} 
    return render(request, 'store/home.html', context)


def store_view(request):
    """The main user-facing shop page."""
    data = cartData(request) 
    products = Product.objects.all()
    context = {'products': products, 'cartItems': data['cartItems']} 
    return render(request, 'store/store_front.html', context) 

def product_detail_view(request, pk):
    """Displays the details of a single product."""
    data = cartData(request) 
    product = get_object_or_404(Product, pk=pk)
    images = product.images.all() 
    
    context = {
        'product': product,
        'images': images,
        'cartItems': data['cartItems'],
    }
    return render(request, 'store/product_detail.html', context)


def cart_view(request):
    """Displays the user's shopping cart."""
    data = cartData(request) 
    
    if request.user.is_authenticated:
        customer = get_customer_or_create(request)
        if customer:
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            items = order.orderitem_set.all()
        else:
            items = []
            order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    else:
        # Handle anonymous user data through cookies/session (handled in utils.py)
        items = data['items']
        order = data['order']
        
    context = {'items': items, 'order': order, 'cartItems': data['cartItems']} 
    return render(request, 'store/cart.html', context)


def checkout_view(request):
    """Displays the user's checkout page."""
    data = cartData(request) 
    
    if request.user.is_authenticated:
        customer = get_customer_or_create(request)
        if customer:
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            items = order.orderitem_set.all()
        else:
            items = []
            order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    else:
        # Handle anonymous user data through cookies/session (handled in utils.py)
        items = data['items']
        order = data['order']
        
    context = {'items': items, 'order': order, 'cartItems': data['cartItems']} 
    return render(request, 'store/checkout.html', context) 


def update_item(request):
    """Handles AJAX requests to add, remove, change quantity, or clear the entire cart."""
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Invalid JSON body.'}, safe=False, status=400)
    
    productId = data.get('productId')
    action = data.get('action')
    
    if not action:
         return JsonResponse({'message': 'Missing action.'}, safe=False, status=400)
    
    if request.user.is_authenticated:
        customer = get_customer_or_create(request) 
        
        if not customer:
            return JsonResponse({'message': 'Error retrieving customer profile.'}, safe=False, status=500)
            
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

        # --- LOGIC FOR CLEAR CART ---
        if action == 'clear':
            order.orderitem_set.all().delete()
            
            updated_data = cartData(request) 
            new_cart_items = updated_data['cartItems']
            return JsonResponse({'message': 'Cart successfully cleared.', 'cartItems': new_cart_items}, safe=False)
        # --- END LOGIC FOR CLEAR CART ---
        
        if not productId:
            return JsonResponse({'message': 'Missing productId for add/remove/delete action.'}, safe=False, status=400)
            
        try:
            product = Product.objects.get(id=productId)
        except Product.DoesNotExist:
            return JsonResponse({'message': 'Product not found.'}, safe=False, status=404)
            
        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

        if action == 'add':
            orderItem.quantity += 1
        elif action == 'remove':
            orderItem.quantity -= 1
        elif action == 'delete': 
            orderItem.quantity = 0

        orderItem.save()

        if orderItem.quantity <= 0:
            orderItem.delete()

        updated_data = cartData(request) 
        new_cart_items = updated_data['cartItems']
        
        return JsonResponse({'message': 'Item was updated', 'cartItems': new_cart_items}, safe=False)
    
    return JsonResponse({'message': 'User is not authenticated (requires cookie handling logic).'}, safe=False, status=403)


def process_order(request):
    """Handles the final submission of an order from the checkout page."""
    
    transaction_id = timezone.now().timestamp() 
    data = json.loads(request.body)
    
    if request.user.is_authenticated:
        customer = get_customer_or_create(request)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        
        # --- 1. Security Check ---
        total = float(data['form']['total'])
        # Check against the server-calculated total
        if round(total, 2) != round(order.get_cart_total, 2):
             print(f"SECURITY ALERT: Total mismatch! Client: {total}, Server: {order.get_cart_total}")
             return JsonResponse('Total mismatch', safe=False, status=400)
             
        # --- 2. Finalize Order ---
        order.transaction_id = transaction_id
        order.complete = True
        order.save()
        
        # --- 3. Deduct Stock and Log Sales ---
        for item in order.orderitem_set.all():
            item.product.stock_quantity -= item.quantity
            item.product.save()
            
            # Log the successful sale/stock deduction (Optional but helpful)
            ActivityLog.objects.create(
                user=request.user,
                action_type='ORDER_COMPLETED',
                description=f"Order {order.id} sold {item.quantity} units of '{item.product.name}'. Stock reduced to {item.product.stock_quantity}.",
                object_id=item.product.pk,
                object_repr=item.product.name
            )
        
        # --- 4. Save Shipping Address (if shipping is required) ---
        if order.shipping:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
                country=data['shipping']['country'],
            )
            
        return JsonResponse('Payment submitted and Order Completed.', safe=False)

    else:
        # Handle anonymous user checkout (requires more complex cookie logic)
        return JsonResponse('User not logged in. Anonymous checkout is not yet implemented.', safe=False, status=403)


# --- PORTAL/ADMIN VIEWS (SECURED WITH @user_passes_test) ---

@login_required(login_url=PORTAL_LOGIN_URL)
@user_passes_test(is_staff_user, login_url=PORTAL_LOGIN_URL)
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product_name = product.name
    product_id = product.pk
    
    if request.method == 'POST':
        product.delete()
        
        # --- LOG: Product Deleted ---
        ActivityLog.objects.create(
            user=request.user,
            action_type='PRODUCT_DELETED',
            description=f"Product '{product_name}' (ID: {product_id}) was permanently deleted from inventory.",
            object_id=product_id,
            object_repr=product_name
        )
        # ---------------------------
        
        # FIX: Changed to namespaced URL 'portal:inventory_dashboard'
        return redirect('portal:inventory_dashboard') 
    
    # FIX: Changed to namespaced URL 'portal:edit_product'
    return redirect('portal:edit_product', pk=pk) 


@login_required(login_url=PORTAL_LOGIN_URL)
@user_passes_test(is_staff_user, login_url=PORTAL_LOGIN_URL)
def inventory_dashboard(request):
    
    # --- DASHBOARD STATS CALCULATION ---
    
    # 1. Total Products (Calculated via product_sales|length in template, but calculating here is cleaner)
    total_products = Product.objects.count()
    
    # 2. Low Stock Alert (Threshold set to 5)
    LOW_STOCK_THRESHOLD = 5
    low_stock_count = Product.objects.filter(stock_quantity__lte=LOW_STOCK_THRESHOLD).count()
    
    # 3. Pending Orders (Orders not complete)
    pending_orders_count = Order.objects.filter(complete=False).count()
    
    # --- TOP SELLING PRODUCTS ---
    product_sales = Product.objects.annotate(
        total_sold=Sum('orderitem__quantity')
    ).order_by('-total_sold') 
    
    # --- ACTIVITY LOG ---
    latest_activities = ActivityLog.objects.all().order_by('-action_time')[:10] 

    context = {
        'product_sales': product_sales,
        'page_title': 'Inventory Dashboard',
        'latest_activities': latest_activities,
        # --- NEW CONTEXT VARIABLES ---
        'total_products': total_products, 
        'low_stock_count': low_stock_count,
        'pending_orders_count': pending_orders_count,
    }
    return render(request, 'store/inventory_dashboard.html', context)

@login_required(login_url=PORTAL_LOGIN_URL)
@user_passes_test(is_staff_user, login_url=PORTAL_LOGIN_URL)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            new_product = form.save()
            
            # --- LOG: Product Added ---
            ActivityLog.objects.create(
                user=request.user,
                action_type='PRODUCT_ADDED',
                description=f"New product '{new_product.name}' (Price: GHC{new_product.price}, Stock: {new_product.stock_quantity}) was added to inventory.",
                object_id=new_product.pk,
                object_repr=new_product.name
            )
            # ---------------------------
            
            # FIX: Changed to namespaced URL 'portal:inventory_dashboard'
            return redirect('portal:inventory_dashboard') 
    else:
        form = ProductForm()
        
    context = {'form': form, 'page_title': 'Add New Product'}
    return render(request, 'store/add_product.html', context)

@login_required(login_url=PORTAL_LOGIN_URL)
@user_passes_test(is_staff_user, login_url=PORTAL_LOGIN_URL)
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    # --- 1. Store all original values for comparison ---
    original_name = product.name
    original_price = product.price
    original_discount = product.discount_price
    original_stock = product.stock_quantity 
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        image_formset = ImageFormSet(request.POST, request.FILES, instance=product)
        
        if form.is_valid() and image_formset.is_valid():
            
            # Save the product now to get the 'updated_product' instance
            updated_product = form.save() 
            image_formset.save()
            
            logs_created = False
            
            # --- 2. Check and log specific field changes ---
            
            # a) Stock Quantity Change
            if updated_product.stock_quantity != original_stock:
                ActivityLog.objects.create(
                    user=request.user,
                    action_type='STOCK_UPDATED',
                    description=f"Stock for '{updated_product.name}' changed from {original_stock} to {updated_product.stock_quantity}.",
                    object_id=updated_product.pk,
                    object_repr=updated_product.name
                )
                logs_created = True

            # b) Price Change
            if updated_product.price != original_price:
                ActivityLog.objects.create(
                    user=request.user,
                    action_type='PRICE_UPDATED',
                    description=f"Price for '{updated_product.name}' changed from GHC{original_price} to GHC{updated_product.price}.",
                    object_id=updated_product.pk,
                    object_repr=updated_product.name
                )
                logs_created = True
            
            # c) Discount Change
            if updated_product.discount_price != original_discount:
                if updated_product.discount_price:
                    ActivityLog.objects.create(
                        user=request.user,
                        action_type='DISCOUNT_APPLIED',
                        description=f"Discount for '{updated_product.name}' set to GHC{updated_product.discount_price}.",
                        object_id=updated_product.pk,
                        object_repr=updated_product.name
                    )
                else:
                    ActivityLog.objects.create(
                        user=request.user,
                        action_type='DISCOUNT_REMOVED',
                        description=f"Discount for '{updated_product.name}' was removed (was GHC{original_discount}).",
                        object_id=updated_product.pk,
                        object_repr=updated_product.name
                    )
                logs_created = True
            
            # d) General Product Update (only if name changed or if other changes occurred but weren't specific logs)
            # The logic below ensures a log is created if the name changed OR if no specific log was created above.
            if updated_product.name != original_name or not logs_created:
                ActivityLog.objects.create(
                    user=request.user,
                    action_type='PRODUCT_UPDATED',
                    description=f"General details for product '{updated_product.name}' were modified.",
                    object_id=updated_product.pk,
                    object_repr=updated_product.name
                )
            
            # FIX: Changed to namespaced URL 'portal:inventory_dashboard'
            return redirect('portal:inventory_dashboard') 
    else:
        form = ProductForm(instance=product)
        image_formset = ImageFormSet(instance=product) 
        
    context = {
        'form': form, 
        'product': product,
        'image_formset': image_formset, 
        'page_title': f'Edit Product: {product.name}'
    }
    return render(request, 'store/edit_product.html', context)


# NEW VIEW: All Activity Log
@login_required(login_url=PORTAL_LOGIN_URL)
@user_passes_test(is_staff_user, login_url=PORTAL_LOGIN_URL)
def all_activity_log_view(request):
    logs = ActivityLog.objects.all().order_by('-action_time')
    
    # 1. Date Range Filtering
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        # Filter logs from the start_date (inclusive)
        logs = logs.filter(action_time__date__gte=start_date)
        
    if end_date:
        # Filter logs up to the end_date (inclusive)
        logs = logs.filter(action_time__date__lte=end_date)
        
    # 2. Keyword Search Filtering (Searches in description and user username)
    keyword = request.GET.get('keyword')
    if keyword:
        # Use models.Q for complex lookups (OR logic)
        logs = logs.filter(
            models.Q(description__icontains=keyword) |
            models.Q(user__username__icontains=keyword)
        ).distinct()
        
    context = {
        'page_title': 'All Activity Logs',
        'activity_logs': logs,
        'start_date': start_date,
        'end_date': end_date,
        'keyword': keyword,
    }
    return render(request, 'store/all_activity_log.html', context)
