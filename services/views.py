# services/views.py (FINAL COMPLETE CODE with Activity Loggers)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import F 

# CRITICAL: Import ActivityLog from the store app
from store.models import Customer, ActivityLog 

# FIX: Import STATUS_CHOICES from models for use in the view
from .models import ServiceRequest, QuoteMessage, STATUS_CHOICES 
from .forms import ServiceRequestForm, AttachmentFormSet 


# --- Utility (Must exist for user linking) ---
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
# ---------------------------------------------

# --- 0. Service Home View ---
def service_home(request):
    """The main landing page for service-related information."""
    context = {} 
    return render(request, 'services/service_home.html', context)


# --- 1. Customer: Submit New Service Request ---
def add_service_request(request):
    """Allows customers to submit a new service request."""
    empty_instance = ServiceRequest() 
    
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST) 
        formset = AttachmentFormSet(request.POST, request.FILES, instance=empty_instance) 
        
        if form.is_valid() and formset.is_valid():
            new_request = form.save(commit=False)
            
            if request.user.is_authenticated:
                new_request.customer = get_customer_or_create(request)
            
            new_request.save()
            
            # Re-instantiate the formset with the *saved* instance for saving attachments
            formset = AttachmentFormSet(request.POST, request.FILES, instance=new_request)

            # Save the formset (attachments)
            formset.save() 
            
            # Redirect to the customer's list
            return redirect(reverse('services:customer_requests_list')) 
        
    else:
        initial_data = {}
        if request.user.is_authenticated:
            customer = get_customer_or_create(request)
            if customer:
                initial_data['customer_name'] = customer.name
                initial_data['contact_email'] = customer.email

        form = ServiceRequestForm(initial=initial_data)
        formset = AttachmentFormSet(instance=empty_instance) 

    context = {'form': form, 'formset': formset}
    return render(request, 'services/add_request.html', context)


# --- 2A. Staff/Admin: List ALL Service Requests ---
@login_required 
def staff_requests_list(request):
    """Displays a list of all service requests, restricted to staff."""
    if not request.user.is_staff:
        # Redirect non-staff to their personal request list
        return redirect(reverse('services:customer_requests_list')) 
        
    requests_list = ServiceRequest.objects.all().order_by('-date_requested')
    
    context = {
        'requests_list': requests_list,
        'page_title': 'Staff: All Service Requests'
    }
    return render(request, 'services/requests_list.html', context)


# --- 2B. Customer: List ONLY Their Service Requests (THE MISSING FUNCTION) ---
@login_required 
def customer_requests_list(request):
    """Displays a list of service requests belonging only to the logged-in customer."""
    customer = get_customer_or_create(request)
    
    # Filter requests where the customer matches the logged-in user
    requests_list = ServiceRequest.objects.filter(customer=customer).order_by('-date_requested')
    
    context = {
        'requests_list': requests_list,
        'page_title': 'Your Service Requests'
    }
    return render(request, 'services/customer_requests_list.html', context)


# --- 3A. Customer: Dedicated Request Chat View ---
@login_required 
def customer_service_request_chat(request, pk):
    """Handles the chat interface for a service request for the Customer."""
    service_request = get_object_or_404(ServiceRequest, pk=pk)
    
    # SECURITY FIX: Only redirect if the user is NOT staff AND they are NOT the request owner.
    if not request.user.is_staff and (service_request.customer is None or service_request.customer.user != request.user):
         return redirect(reverse('services:customer_requests_list'))

    # --- HANDLE FORM SUBMISSION ---
    if request.method == 'POST':
        message_text = request.POST.get('message_text')
        
        if message_text:
            # Save the new message 
            QuoteMessage.objects.create(
                request=service_request,
                message=message_text,
                sender='CUSTOMER',
                user=request.user 
            )
            return redirect(reverse('services:customer_chat', kwargs={'pk': pk})) # Use the new URL name

    context = {
        'request': service_request,
        'messages': service_request.messages.all().order_by('timestamp'),
    }
    
    # Renders the dedicated customer template
    return render(request, 'services/service_request_chat.html', context)


# --- 3B. Staff/Admin: Dedicated Request Chat View (WITH LOGGING) ---
@login_required 
def staff_service_request_chat(request, pk):
    """Handles the chat interface for a service request for Staff/Admin."""
    service_request = get_object_or_404(ServiceRequest, pk=pk)
    
    if not request.user.is_staff:
         return redirect(reverse('services:customer_requests_list')) # Deny non-staff

    # --- HANDLE FORM SUBMISSION ---
    if request.method == 'POST':
        
        # 1. Handle Status Update (Staff only)
        if 'update_status' in request.POST:
            new_status = request.POST.get('new_status')
            if new_status and new_status in dict(STATUS_CHOICES):
                
                old_status_display = service_request.get_status_display()
                service_request.status = new_status
                service_request.save()
                
                # Log status change in QuoteMessage
                QuoteMessage.objects.create(
                    request=service_request,
                    message=f"System: Status changed from {old_status_display} to {service_request.get_status_display()} by {request.user.username}.",
                    sender='ADMIN',
                    user=request.user 
                )
                
                # --- LOG: Activity Log Entry ---
                ActivityLog.objects.create(
                    user=request.user,
                    action_type='REQUEST_STATUS_UPDATED',
                    description=f"Status for Service Request #{pk} changed to {service_request.get_status_display()}.",
                    object_id=pk,
                    object_repr=f"Service Request #{pk}"
                )
                # -------------------------------

            return redirect(reverse('services:staff_chat', kwargs={'pk': pk}))


        # 2. Handle Chat Message Submission (Staff only)
        message_text = request.POST.get('message_text')
        
        if message_text:
            QuoteMessage.objects.create(
                request=service_request,
                message=message_text,
                sender='ADMIN',
                user=request.user 
            )
            
            # Automatically update status if replying to PENDING request
            if service_request.status == 'PENDING':
                service_request.status = 'IN_PROGRESS'
                service_request.save()
            
            # --- LOG: Activity Log Entry ---
            ActivityLog.objects.create(
                user=request.user,
                action_type='REQUEST_REPLY_SENT',
                description=f"Sent chat reply (Quote/Info) to Service Request #{pk}.",
                object_id=pk,
                object_repr=f"Service Request #{pk}"
            )
            # -------------------------------
            
            return redirect(reverse('services:staff_chat', kwargs={'pk': pk}))

    context = {
        'request': service_request,
        'messages': service_request.messages.all().order_by('timestamp'),
        'status_choices': STATUS_CHOICES, # Passed to the staff template
    }
    
    return render(request, 'services/service_request_chat_staff.html', context)