# services/models.py (FINAL)

from django.db import models
from django.contrib.auth.models import User
from store.models import Customer 

# Choices for the status field
STATUS_CHOICES = (
    ('PENDING', 'Pending Review'),
    ('QUOTED', 'Quote Sent'),
    ('ACCEPTED', 'Quote Accepted'),
    ('COMPLETE', 'Job Completed'),
    ('CANCELLED', 'Cancelled'),
    ('IN_PROGRESS', 'In Progress'),
)

# Choices for the sender field in QuoteMessage
SENDER_CHOICES = (
    ('ADMIN', 'Admin'),
    ('CUSTOMER', 'Customer'),
)

# 1. Model to capture the initial service request
class ServiceRequest(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    
    customer_name = models.CharField(max_length=200, help_text="Name of the person requesting the service.")
    contact_email = models.EmailField(max_length=254, help_text="Email address for correspondence.")
    
    service_type = models.CharField(max_length=100, help_text="e.g., Camera Repair, Graphic Design, Printing")
    description = models.TextField()
    date_requested = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"Request #{self.id} - {self.service_type}"


# 2. Model for Attachments
class ServiceAttachment(models.Model):
    request = models.ForeignKey(
        ServiceRequest, 
        on_delete=models.CASCADE, 
        related_name='attachments'
    )
    # CRITICAL: Only 'file' is present, which is why the old forms crashed.
    file = models.FileField(upload_to='service_attachments/', null=False, blank=False)
    
    def __str__(self):
        return f"Attachment for Request #{self.request.id}"


# 3. Model for the chat/quote messages between admin and customer
class QuoteMessage(models.Model):
    request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) 
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Msg on Request #{self.request.id} by {self.sender}"