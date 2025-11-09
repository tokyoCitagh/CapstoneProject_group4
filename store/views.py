# store/views.py (FINAL UPDATED - MANUAL AUTHENTICATION LOGIC WITH NEXT/ACTIVE CHECKS)
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum 
from django.db.models import Q 
from django.http import JsonResponse, HttpResponse
from django.forms import inlineformset_factory 
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy 
from django.utils import timezone 
# Ensure these are imported:
from django.contrib.auth import logout as auth_logout, authenticate, login 
import json 
from django.contrib import messages 

# --- CRITICAL IMPORTS ---
from store.models import Product, Order, OrderItem, ProductImage, Customer, ShippingAddress, ActivityLog 
from store.utils import cartData 
from store.forms import ProductForm 
from services.models import ServiceRequest, QuoteMessage, ServiceAttachment 
from services.forms import ServiceRequestForm, AttachmentFormSet 
# FIX: Import standard Django AuthenticationForm
from django.contrib.auth.forms import AuthenticationForm
# CRITICAL FIX: Import the allauth EmailAddress model
from allauth.account.models import EmailAddress
# -------------------------------------------------------------------------------------

# Define the Image Formset (E-commerce related)
ImageFormSet = inlineformset_factory(
    Product, 
    ProductImage, 
    fields=('image',), 
    extra=1, 
    can_delete=True
)

# --- UTILITY FUNCTIONS ---
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


def is_staff_user(user):
    """Checks if the user is active and has staff privileges."""
    return user.is_active and user.is_staff

# CRITICAL: Use reverse_lazy('portal:login') for consistent redirects
PORTAL_LOGIN_URL = reverse_lazy('portal:login') 
PORTAL_DASHBOARD_URL = reverse_lazy('portal:inventory_dashboard') # Define the success URL

# --- FIX: Custom view to handle manual authentication ---
def portal_login_view(request):
    """Handles both rendering and manual processing of the staff login form."""
    
    # 1. Early exit if staff is already logged in
    if request.user.is_authenticated and is_staff_user(request.user):
        return redirect(PORTAL_DASHBOARD_URL)

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Authenticate the user manually
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Check if the authenticated user has staff and active privileges
                if user.is_staff and user.is_active:
                    login(request, user)
                    
                    # Log the successful staff login
                    ActivityLog.objects.create(
                        user=user,
                        action_type='STAFF_LOGIN',
                        description=f"Successful staff login to the portal.",
                    )
                    
                    # Use the 'next' parameter if present, otherwise default to dashboard
                    next_url = request.GET.get('next') or PORTAL_DASHBOARD_URL
                    return redirect(next_url)
                
                # Fails authentication but user exists
                elif not user.is_staff:
                    messages.error(request, "Login failed: Your account does not have staff privileges.")
                elif not user.is_active:
                    messages.error(request, "Login failed: Your staff account is currently inactive.")
            else:
                # Authentication failed (bad credentials)
                messages.error(request, "Invalid username or password.")
        
        # If form is not valid or authentication failed, re-render with errors
        context = {'form': form}
        return render(request, 'account/login_portal.html', context)
        
    else:
        # GET request: render empty form
        form = AuthenticationForm() 
        
    context = {'form': form}
    return render(request, 'account/login_portal.html', context) 
# ---------------------------------------------------------------


def account_login_view(request):
    """Replacement login view to handle /accounts/login/ when allauth causes issues in production.

    This uses Django's AuthenticationForm to authenticate users and renders the
    existing `templates/account/login.html` which expects a `form` and
    `redirect_field_value` context variables.
    """
    from django.conf import settings

    # If already authenticated, redirect to configured LOGIN_REDIRECT_URL
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # honor 'next' parameter
            next_url = request.POST.get('next') or request.GET.get('next')
            return redirect(next_url or settings.LOGIN_REDIRECT_URL)
    else:
        form = AuthenticationForm(request)

    redirect_field_name = 'next'
    redirect_field_value = request.GET.get(redirect_field_name, '')

    context = {
        'form': form,
        'redirect_field_name': redirect_field_name,
        'redirect_field_value': redirect_field_value,
    }
    return render(request, 'account/login.html', context)



# --- CUSTOMER ACCOUNT VIEWS (ADDED FOR EMAIL DATE FIX) ---
@login_required
def custom_email_list_view(request):
    """
    Custom view to list user emails, fetching objects directly to ensure 
    'date_created' is available for display in the simplified 'email.html' template.
    """
    
    # Fetch all EmailAddress objects related to the logged-in user
    emailaddresses = EmailAddress.objects.filter(user=request.user).order_by('primary', 'verified')
    
    # Pass necessary context for the allauth template
    context = {
        'emailaddresses': emailaddresses,
        # 'form' is required by the original email.html template structure
        'form': None, 
    }
    return render(request, 'account/email.html', context)
# --------------------------------------------------------


# -------------------------------------------------------------------------------------
# --- USER-FACING E-COMMERCE VIEWS ---
# -------------------------------------------------------------------------------------

def home_view(request):
    """The main landing page for the site."""
    data = cartData(request) 
    # Temporary hotfix: if running in production (DEBUG=False) bypass template
    # rendering to avoid fatal TemplateSyntaxError during emergency deploys.
    from django.conf import settings
    if not getattr(settings, 'DEBUG', False):
        return HttpResponse(
            "<h1>Site temporarily unavailable</h1><p>Applying emergency hotfix — please try again shortly.</p>",
            content_type='text/html',
            status=503,
        )

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
            
            # Log the successful sale/stock deduction 
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
        # Handle anonymous user checkout (not implemented here)
        return JsonResponse('User not logged in. Anonymous checkout is not yet implemented.', safe=False, status=403)


# -------------------------------------------------------------------------------------
# --- PORTAL/ADMIN VIEWS (SECURED WITH @user_passes_test) ---
# -------------------------------------------------------------------------------------

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
        
        return redirect('portal:inventory_dashboard') 
    
    return redirect('portal:edit_product', pk=pk) 


@login_required(login_url=PORTAL_LOGIN_URL)
@user_passes_test(is_staff_user, login_url=PORTAL_LOGIN_URL)
def inventory_dashboard(request):
    
    # --- DASHBOARD STATS CALCULATION ---
    total_products = Product.objects.count()
    
    # Low Stock Alert (Threshold set to 5)
    LOW_STOCK_THRESHOLD = 5
    low_stock_count = Product.objects.filter(stock_quantity__lte=LOW_STOCK_THRESHOLD).count()
    
    # Pending Orders (Orders not complete)
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
                action_type = 'DISCOUNT_APPLIED' if updated_product.discount_price else 'DISCOUNT_REMOVED'
                description = f"Discount for '{updated_product.name}' set to GHC{updated_product.discount_price}." if updated_product.discount_price else f"Discount for '{updated_product.name}' was removed (was GHC{original_discount})."
                ActivityLog.objects.create(
                    user=request.user,
                    action_type=action_type,
                    description=description,
                    object_id=updated_product.pk,
                    object_repr=updated_product.name
                )
                logs_created = True
            
            # d) General Product Update
            if updated_product.name != original_name or not logs_created:
                ActivityLog.objects.create(
                    user=request.user,
                    action_type='PRODUCT_UPDATED',
                    description=f"General details for product '{updated_product.name}' were modified.",
                    object_id=updated_product.pk,
                    object_repr=updated_product.name
                )
            
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


@login_required(login_url=PORTAL_LOGIN_URL)
@user_passes_test(is_staff_user, login_url=PORTAL_LOGIN_URL)
def all_activity_log_view(request):
    logs = ActivityLog.objects.all().order_by('-action_time')
    
    # 1. Date Range Filtering
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        logs = logs.filter(action_time__date__gte=start_date)
    if end_date:
        logs = logs.filter(action_time__date__lte=end_date)
        
    # 2. Keyword Search Filtering
    keyword = request.GET.get('keyword')
    if keyword:
        logs = logs.filter(
            Q(description__icontains=keyword) |
            Q(user__username__icontains=keyword)
        ).distinct()
        
    context = {
        'page_title': 'All Activity Logs',
        'activity_logs': logs,
        'start_date': start_date,
        'end_date': end_date,
        'keyword': keyword,
    }
    return render(request, 'store/all_activity_log.html', context)


# -------------------------------------------------------------------------------------
# --- USER-FACING SERVICE VIEWS ---
# -------------------------------------------------------------------------------------

def service_home(request):
    data = cartData(request)
    context = {'cartItems': data['cartItems']}
    return render(request, 'services/service_home.html', context)


@login_required 
def add_service_request(request):
    data = cartData(request)
    customer = get_customer_or_create(request)
    
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST) 
        attachment_formset = AttachmentFormSet(request.POST, request.FILES)

        if form.is_valid() and attachment_formset.is_valid():
            new_request = form.save(commit=False)
            new_request.customer = customer
            new_request.save()
            
            attachment_formset.instance = new_request 
            attachment_formset.save()
            
            messages.success(request, 'Your service request has been submitted! We will respond shortly.')
            return redirect('services:customer_requests_list') 
        else:
            messages.error(request, 'There was an error in your form submission. Please check the details.')
            
    else:
        form = ServiceRequestForm()
        attachment_formset = AttachmentFormSet()
        
    context = {
        'form': form,
        'attachment_formset': attachment_formset,
        'page_title': 'Submit Service Request',
        'cartItems': data['cartItems'],
    }
    return render(request, 'services/add_request.html', context)

@login_required
def customer_requests_list(request):
    """Displays a list of service requests submitted by the logged-in customer."""
    customer = get_customer_or_create(request)
    requests = ServiceRequest.objects.filter(customer=customer).order_by('-date_requested')
    
    data = cartData(request)
    context = {
        'page_title': 'My Service Requests',
        'requests_list': requests, 
        'cartItems': data['cartItems'],
    }
    return render(request, 'services/customer_requests_list.html', context)

@login_required
def customer_service_request_chat(request, pk):
    """Handles the customer view and chat for a single service request."""
    customer = get_customer_or_create(request)
    service_request = get_object_or_404(
        ServiceRequest.objects.prefetch_related('messages', 'attachments'), 
        pk=pk, 
        customer=customer
    )
    
    if request.method == 'POST':
        message_text = request.POST.get('message')
        if message_text:
            QuoteMessage.objects.create(
                request=service_request,
                user=request.user,
                sender='CUSTOMER',
                message=message_text
            )
            messages.success(request, "Reply sent successfully.")
            return redirect('services:customer_chat', pk=pk)
            
    data = cartData(request)
    context = {
        'page_title': f'Request #{pk} - Chat',
        'service_request': service_request,
        'messages': service_request.messages.all().order_by('timestamp'),
        'attachments': service_request.attachments.all(),
        'cartItems': data['cartItems'],
    }
    return render(request, 'services/service_request_chat.html', context)


# -------------------------------------------------------------------------------------
# --- PORTAL/ADMIN SERVICE VIEWS (SECURED) ---
# -------------------------------------------------------------------------------------

@login_required(login_url=PORTAL_LOGIN_URL)
@user_passes_test(is_staff_user, login_url=PORTAL_LOGIN_URL)
def staff_requests_list(request):
    """Displays a list of all Service Requests for staff review."""
    requests = ServiceRequest.objects.all().order_by('-date_requested')
    context = {
        'page_title': 'Service Requests List',
        'requests': requests,
    }
    return render(request, 'services/requests_list.html', context)


@login_required(login_url=PORTAL_LOGIN_URL)
@user_passes_test(is_staff_user, login_url=PORTAL_LOGIN_URL)
def staff_service_request_chat(request, pk):
    """Handles the staff view for a single service request, including quoting and chat."""
    service_request = get_object_or_404(
        ServiceRequest.objects.prefetch_related('messages', 'attachments'), 
        pk=pk
    )
    
    if request.method == 'POST':
        message_text = request.POST.get('message')
        new_status = request.POST.get('new_status') 
        
        if message_text:
            QuoteMessage.objects.create(
                request=service_request,
                user=request.user,
                sender='ADMIN',
                message=message_text
            )
            if service_request.status in ['PENDING', 'QUOTED']:
                service_request.status = 'IN_PROGRESS'
                service_request.save()
            
            messages.success(request, "Reply sent successfully.")
            return redirect('portal:staff_chat', pk=pk)
            
        if new_status and new_status != service_request.status:
            service_request.status = new_status
            service_request.save()
            messages.success(request, f"Request status updated to {new_status}.")
            return redirect('portal:staff_chat', pk=pk)
    
    status_choices = ServiceRequest._meta.get_field('status').choices
            
    context = {
        'page_title': f'Request #{pk} - {service_request.service_type}',
        'service_request': service_request,
        'messages': service_request.messages.all().order_by('timestamp'),
        'attachments': service_request.attachments.all(),
        'STATUS_CHOICES': status_choices, 
    }
    return render(request, 'services/service_request_chat_staff.html', context)