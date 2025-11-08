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