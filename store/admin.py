from django.contrib import admin
from .models import Product, Category # Import the Product and Category models

# Define the custom ModelAdmin class for Category
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

# Define the custom ModelAdmin class for Product
class ProductAdmin(admin.ModelAdmin):
    # Change list_display to use 'name', 'price', and 'digital'
    list_display = ('name', 'price', 'digital') 
    
    # Keep the search functionality
    search_fields = ('name',)
    filter_horizontal = ('categories',)  # Better UI for many-to-many

# Register the models with their ModelAdmin
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)

# You would also register your other models here (e.g., Order, Customer)
# from .models import Order, Customer 
# admin.site.register(Order)
# admin.site.register(Customer)