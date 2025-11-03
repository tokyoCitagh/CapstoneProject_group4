# services/forms.py (Updated with clear black borders)

from django import forms
from django.forms.models import inlineformset_factory
from .models import ServiceRequest, ServiceAttachment 


# Base Service Request Form
class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ['customer_name', 'contact_email', 'service_type', 'description'] 
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'border-2 border-black p-2 rounded-lg w-full'}),
            'contact_email': forms.EmailInput(attrs={'class': 'border-2 border-black p-2 rounded-lg w-full'}),
            'service_type': forms.TextInput(attrs={'class': 'border-2 border-black p-2 rounded-lg w-full'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'border-2 border-black p-2 rounded-lg w-full'}),
        }

# Define a form for the attachment model
class ServiceAttachmentForm(forms.ModelForm):
    # The file input is styled primarily through CSS/JS in the template, 
    # but we can ensure the widget has basic classes.
    file = forms.FileField(
        label='Attachment', 
        widget=forms.FileInput(attrs={'accept': 'image/*', 'class': 'border-2 border-black p-2 rounded-lg w-full'}),
        required=False  
    )

    class Meta:
        model = ServiceAttachment
        fields = ['file']


# Final Formset Definition
AttachmentFormSet = inlineformset_factory(
    ServiceRequest, 
    ServiceAttachment, 
    form=ServiceAttachmentForm, 
    fields=('file',),
    extra=4, 
    max_num=4, 
    can_delete=False, 
)