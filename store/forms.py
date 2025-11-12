# store/forms.py (FINAL UPDATED CODE including custom forms and LOGIN FIX)

from django import forms
from django.contrib.auth.forms import UserCreationForm 
from .models import Product, ProductImage 

# Import allauth's base form for overriding the login view
from allauth.account.forms import LoginForm as AllauthLoginForm 
from django.utils.translation import gettext_lazy as _

# -------------------------------------------------------------------
# 0. CRITICAL LOGIN FIX: Custom Form to force the 'password' field
# -------------------------------------------------------------------
class CustomLoginForm(AllauthLoginForm):
    """
    A custom form that explicitly ensures the 'password' field is present
    and orders the fields correctly, bypassing the stubborn allauth internal logic.
    """
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'placeholder': _('Password')})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure the field order is correct for 'username_email' method
        # Use order_fields (supported in modern Django) instead of the
        # deprecated/invalid `keyOrder` attribute which raises AttributeError
        # when set on the underlying OrderedDict.
        try:
            self.order_fields(['login', 'password', 'remember'])
        except Exception:
            # Fallback: ensure keys exist and attempt a safe reorder
            field_keys = ['login', 'password', 'remember']
            ordered = {k: self.fields[k] for k in field_keys if k in self.fields}
            for k in list(self.fields.keys()):
                if k not in ordered:
                    ordered[k] = self.fields[k]
            self.fields = type(self.fields)(ordered)
        
# -------------------------------------------------------------------
# 1. FIX: Custom Registration Form to ADD Email Field
# -------------------------------------------------------------------
class CustomUserCreationForm(UserCreationForm):
    """
    A custom form that adds the email field to the standard UserCreationForm.
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
# 2. ProductForm Definition 
# -------------------------------------------------------------------
class ProductForm(forms.ModelForm):
    """
    Form used for the Add Product and Edit Product administrative views.
    """
    class Meta:
        model = Product
        fields = ['name', 'price', 'discount_price', 'stock_quantity', 'digital', 'categories'] 
        labels = {
            'name': 'Product Name',
            'price': 'Price (GHC)',
            'discount_price': 'Discount Price (GHC)',
            'stock_quantity': 'Stock Quantity Remaining',
            'digital': 'Is this a digital product?',
            'categories': 'Categories',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'stock_quantity': forms.NumberInput(attrs={'min': 0, 'step': 1}),
            'categories': forms.CheckboxSelectMultiple(),
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

# -------------------------------------------------------------------
# 4. CategoryForm Definition
# -------------------------------------------------------------------
from .models import Category
from django.utils.text import slugify

class CategoryForm(forms.ModelForm):
    """
    Form for creating and editing product categories.
    """
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        label='Assign Products to this Category',
        help_text='Select which products belong to this category'
    )
    
    class Meta:
        model = Category
        fields = ['name', 'description']
        labels = {
            'name': 'Category Name',
            'description': 'Description (Optional)',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Brief description of this category'}),
            'name': forms.TextInput(attrs={'placeholder': 'e.g., Cameras, Lenses, Accessories'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-populate the products field with current category products when editing
        if self.instance.pk:
            self.fields['products'].initial = self.instance.products.all()
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Auto-generate slug from name if not provided
        if not instance.slug:
            instance.slug = slugify(instance.name)
        if commit:
            instance.save()
            # Save the many-to-many relationship
            instance.products.set(self.cleaned_data['products'])
            self.save_m2m()
        return instance