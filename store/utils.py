from .models import Order, Customer # ADDED Customer import

def cartData(request):
    """
    Retrieves the total number of items in the active cart for the current user.
    This function is used to populate the navigation bar counter in base.html.
    """
    if request.user.is_authenticated:
        # Assuming the User model is linked to a Customer model (as per models.py)
        try:
            # Safely get the customer linked to the current logged-in user
            customer = request.user.customer 
        except Customer.DoesNotExist: # Changed exception type to Customer.DoesNotExist
            # If the user is logged in but has no Customer profile, return 0
            return {'cartItems': 0}

        # Get or create the active, incomplete order (the cart)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        
        # Use the property defined on the Order model
        cartItems = order.get_cart_items
    else:
        # Simplified: Guest users start with 0 items (real implementation uses sessions/cookies)
        cartItems = 0

    return {'cartItems': cartItems}
