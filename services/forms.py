# services/forms.py (Updated with clear black borders)
from django import forms
from django.forms.models import inlineformset_factory
from .models import ServiceRequest, ServiceAttachment 


# Base Service Request Form
class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        # Uses fields confirmed in models.py
        fields = ['customer_name', 'contact_number', 'service_type', 'description'] 
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'border-2 border-black p-2 rounded-lg w-full', 'placeholder': 'Your Full Name'}),
            'contact_number': forms.TextInput(attrs={'class': 'border-2 border-black p-2 rounded-lg w-full', 'placeholder': '+233 XX XXX XXXX'}),
            'service_type': forms.TextInput(attrs={'class': 'border-2 border-black p-2 rounded-lg w-full', 'placeholder': 'e.g., Camera Repair'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'border-2 border-black p-2 rounded-lg w-full', 'placeholder': 'Describe your service needs in detail...'}),
        }
        labels = {
            'customer_name': 'Your Name',
            'contact_number': 'Contact Number',
            'service_type': 'Service Requested',
        }


# Define a form for the attachment model
class ServiceAttachmentForm(forms.ModelForm):
    class Meta:
        model = ServiceAttachment
        # Only 'file' is used, matching the model
        fields = ['file'] 
        widgets = {
            'file': forms.FileInput(attrs={'accept': 'image/*,application/pdf', 'class': 'border-2 border-black p-2 rounded-lg w-full'}),
        }


# Final Formset Definition
AttachmentFormSet = inlineformset_factory(
    ServiceRequest, 
    ServiceAttachment, 
    form=ServiceAttachmentForm, 
    # Only 'file' is used, matching the model and form
    fields=('file',), 
    extra=4,  # Show 4 file input fields by default
    max_num=4, 
    can_delete=False, 
)