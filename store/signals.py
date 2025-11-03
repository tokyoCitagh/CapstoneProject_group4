# store/signals.py

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Customer # Assuming your Customer model is here

@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):
    """
    Creates a Customer object when a new User is registered.
    """
    if created:
        # Only create if the user does not already have a customer profile
        Customer.objects.get_or_create(
            user=instance,
            # Provide default values for required fields like 'name' and 'email'
            defaults={
                'name': instance.username,
                'email': instance.email or ''
            }
        )

# Optional: Ensure the customer profile is saved if the user is saved
@receiver(post_save, sender=User)
def save_customer_profile(sender, instance, **kwargs):
    if hasattr(instance, 'customer'):
        instance.customer.save()