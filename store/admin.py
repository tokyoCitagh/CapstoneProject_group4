from django.contrib import admin
from .models import Product # Import the Product model

# Define the custom ModelAdmin class for Product
class ProductAdmin(admin.ModelAdmin):
    # Change list_display to use 'name', 'price', and 'digital'
    list_display = ('name', 'price', 'digital') 
    
    # Keep the search functionality
    search_fields = ('name',)

# Register the model with its ModelAdmin
admin.site.register(Product, ProductAdmin)

# You would also register your other models here (e.g., Order, Customer)
# from .models import Order, Customer 
# admin.site.register(Order)
# admin.site.register(Customer)