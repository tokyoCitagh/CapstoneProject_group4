import os
from django.templatetags.static import static


def static_cloudinary_urls(request):
    """Provide safe static/cloudinary URLs to templates.

    This context processor prefers explicit STATIC_CLOUDINARY_* environment
    variables (set during deployment). If they're not present it falls back
    to the local `{% static %}` paths so templates never need to call
    template tags inside filters (which causes TemplateSyntaxError).
    """
    # Read any Cloudinary-provided static URLs from environment (deployment)
    imj1 = os.environ.get('STATIC_CLOUDINARY_IMJ1_URL')
    imj2 = os.environ.get('STATIC_CLOUDINARY_IMJ2_URL')
    imj3 = os.environ.get('STATIC_CLOUDINARY_IMJ3_URL')
    imj4 = os.environ.get('STATIC_CLOUDINARY_IMJ4_URL')
    imjlogo = os.environ.get('STATIC_CLOUDINARY_IMJLOGO_URL')

    # Safe fallbacks using django's static helper
    safe_imj1 = imj1 if imj1 else static('images/imj1.jpg')
    safe_imj2 = imj2 if imj2 else static('images/imj2.jpg')
    safe_imj3 = imj3 if imj3 else static('images/imj3.jpg')
    safe_imj4 = imj4 if imj4 else static('images/imj4.jpg')
    safe_imjlogo = imjlogo if imjlogo else static('images/imjlogo.webp')

    return {
        'STATIC_CLOUDINARY_IMJ1_URL': imj1,
        'STATIC_CLOUDINARY_IMJ2_URL': imj2,
        'STATIC_CLOUDINARY_IMJ3_URL': imj3,
        'STATIC_CLOUDINARY_IMJ4_URL': imj4,
        'STATIC_CLOUDINARY_IMJLOGO_URL': imjlogo,
        'SAFE_STATIC_CLOUDINARY_IMJ1_URL': safe_imj1,
        'SAFE_STATIC_CLOUDINARY_IMJ2_URL': safe_imj2,
        'SAFE_STATIC_CLOUDINARY_IMJ3_URL': safe_imj3,
        'SAFE_STATIC_CLOUDINARY_IMJ4_URL': safe_imj4,
        'SAFE_STATIC_CLOUDINARY_IMJLOGO_URL': safe_imjlogo,
    }
# store/context_processors.py

from .models import Order, Customer

def cart_count(request):
    """Adds the active cart's item count to the context of every request."""
    # Initialize cart_items to 0 as a default value
    cart_items = 0
    
    if request.user.is_authenticated:
        try:
            # Safely get the customer profile
            customer = Customer.objects.get(user=request.user)
            
            # Get the incomplete cart order
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            
            # Use the method defined in the Order model
            cart_items = order.get_cart_items
            
        except Customer.DoesNotExist:
            # This handles cases where a User exists but the signal might have failed
            # We can safely assume 0 items if the profile isn't ready.
            pass
        except Exception as e:
            # Handle other potential database issues gracefully
            print(f"Error loading cart context: {e}")
            pass

    # Return the data dictionary that will be merged with the template context
    return {
        'cart_items': cart_items,
    }