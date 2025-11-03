# store/forms.py (FINAL UPDATED CODE including custom forms)

from django import forms
from django.contrib.auth.forms import UserCreationForm # <-- Import UserCreationForm
from .models import Product, ProductImage # Import necessary models

# -------------------------------------------------------------------
# 1. FIX: Custom Registration Form to ADD Email Field
# -------------------------------------------------------------------
class CustomUserCreationForm(UserCreationForm):
    """
    A custom form that adds the email field to the standard UserCreationForm.
    This is necessary for email confirmation and password reset to work correctly.
    """
    email = forms.EmailField(
        required=True,
        label='Email Address',
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'})
    )

    class Meta(UserCreationForm.Meta):
        # Extend the default fields and include 'email'
        fields = UserCreationForm.Meta.fields + ('email',)


# -------------------------------------------------------------------
# 2. ProductForm Definition (as you provided)
# -------------------------------------------------------------------
class ProductForm(forms.ModelForm):
    """
    Form used for the Add Product and Edit Product administrative views.
    """
    class Meta:
        model = Product
        # MODIFIED: Added 'stock_quantity' field
        fields = ['name', 'price', 'discount_price', 'stock_quantity', 'digital'] 
        labels = {
            'name': 'Product Name',
            'price': 'Price (GHC)',
            'discount_price': 'Discount Price (GHC)',
            'stock_quantity': 'Stock Quantity Remaining',
            'digital': 'Is this a digital product?',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            # Use NumberInput for better mobile experience and validation
            'stock_quantity': forms.NumberInput(attrs={'min': 0, 'step': 1}), 
        }

# -------------------------------------------------------------------
# 3. ProductImageForm for Formset
# -------------------------------------------------------------------
class ProductImageForm(forms.ModelForm):
    """
    Form used for the inline formset in product management.
    """
    class Meta:
        model = ProductImage
        fields = ('image',)
        labels = {
            'image': 'Product Image File',
        }