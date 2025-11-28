from .models import Order, Customer
import logging
from django.db import DatabaseError
from django.db.utils import ProgrammingError, OperationalError

logger = logging.getLogger(__name__)


def cartData(request):
    """Return a consistent cart data dict with keys: 'items', 'order', 'cartItems'.

    Views expect these keys for both authenticated and anonymous users.
    For anonymous users we return an empty cart structure (sessions/cookies
    handling can be added later).
    """
    if request.user.is_authenticated:
        try:
            customer = request.user.customer
        except Customer.DoesNotExist:
            # If user has no customer profile yet, return empty cart structure
            return {
                'items': [],
                'order': {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False},
                'cartItems': 0,
            }

        try:
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            items = order.orderitem_set.all()
            cartItems = order.get_cart_items
            return {'items': items, 'order': order, 'cartItems': cartItems}
        except (ProgrammingError, OperationalError, DatabaseError) as e:
            # Defensive fallback: if the DB schema is out-of-sync (e.g. missing column),
            # return a minimal cart structure instead of raising a 500. This allows
            # the site to stay up while migrations are applied.
            logger.warning('cartData DB error; returning empty cart fallback: %s', e)
            return {
                'items': [],
                'order': {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False, 'shipping_fee': 0},
                'cartItems': 0,
            }

    # Anonymous / guest user: return empty cart placeholders
    return {
        'items': [],
        'order': {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False},
        'cartItems': 0,
    }
