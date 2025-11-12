# store/models.py (FINAL UPDATED)
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal 

# NEW MODEL: ActivityLog
class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action_time = models.DateTimeField(auto_now_add=True)
    action_type = models.CharField(max_length=50) # e.g., 'PRODUCT_ADDED', 'STOCK_UPDATED', 'DISCOUNT_APPLIED'
    description = models.TextField() # Detailed description of the action (e.g., "Stock changed from 50 to 100")
    
    # Optional: Link to a specific object (e.g., Product or ServiceRequest)
    object_id = models.IntegerField(null=True, blank=True)
    object_repr = models.CharField(max_length=200, null=True, blank=True) 

    class Meta:
        ordering = ['-action_time']
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"

    def __str__(self):
        return f"[{self.action_time.strftime('%Y-%m-%d %H:%M')}] {self.user.username if self.user else 'System'} - {self.action_type}"

# 1. Customer Model: Extends Django's built-in User
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name if self.name else 'Guest Customer'

# NEW MODEL: Category for organizing products
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    display_order = models.IntegerField(default=0, help_text="Lower numbers appear first on the storefront")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

# 2. Product Model: The items you sell
class Product(models.Model):
    name = models.CharField(max_length=200, null=True)
    price = models.DecimalField(max_digits=7, decimal_places=2) 
    digital = models.BooleanField(default=False, null=True, blank=True)
    
    # NEW FIELD: Optional discount price
    discount_price = models.DecimalField(
        max_digits=7, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    
    # --- ADDED: Inventory Stock Field ---
    stock_quantity = models.IntegerField(default=0)
    # ------------------------------------
    
    # Many-to-Many relationship with Category
    categories = models.ManyToManyField(Category, blank=True, related_name='products')

    def __str__(self):
        return self.name
    
    # Helper to get the primary image (the one used on the dashboard)
    @property
    def primary_image(self):
        # Assumes ProductImage has related_name='images'
        return self.images.first() 
    
    # Helper property to determine the current selling price
    @property
    def selling_price(self):
        # If discount_price is set AND is lower than the regular price, use it
        if self.discount_price and self.discount_price < self.price:
            return self.discount_price
        return self.price


# NEW MODEL: To allow a Product to have many images
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='images' # Allows access via product.images.all()
    )
    # The actual file field
    image = models.ImageField(upload_to='product_photos/', null=False, blank=False)
    date_uploaded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product.name}"

# 3. Order Model: The shopping cart or completed transaction 
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=True)
    transaction_id = models.CharField(max_length=100, null=True)
    # NEW: More expressive order status and optional expected delivery datetime
    STATUS_PENDING = 'PENDING'
    STATUS_PROCESSING = 'PROCESSING'
    STATUS_SHIPPED = 'SHIPPED'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_SHIPPED, 'Shipped'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    expected_delivery = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)
    
    @property
    def shipping(self):
        # Determines if shipping is required (if any item is NOT digital)
        shipping = False
        orderitems = self.orderitem_set.all()
        for item in orderitems:
            if not item.product.digital:
                shipping = True
        return shipping
    
    @property
    def get_cart_total(self):
        # Sums the total cost across all OrderItems in this Order
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        # Sums the total quantity of all items in this Order
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

# 4. OrderItem Model: Links products to a specific Order
class OrderItem(models.Model):
    # Set to models.SET_NULL so the OrderItem remains if the Product is deleted.
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True) 
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        # Check if product exists before accessing its attribute
        if self.product:
            return self.product.selling_price * self.quantity
        return Decimal('0.00') 

# 5. ShippingAddress Model: Stores delivery information
class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    # CRITICAL: Added 'country' field as it's typically required in checkout forms
    country = models.CharField(max_length=200, null=False, default='Ghana') 
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address