from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class CeleryAccountAdapter(DefaultAccountAdapter):
    """Allauth adapter that enqueues outgoing emails to Celery when a broker
    is configured. Falls back to synchronous send when Celery isn't
    available.
    """

    def send_mail(self, template_prefix, email, context):
        # Store email in session for display on password reset done page
        request = context.get('request')
        if request and hasattr(request, 'session'):
            request.session['password_reset_email'] = email
        
        # TEMPORARY FIX: Railway worker containers cannot reach external SMTP servers
        # Send emails synchronously from web service instead of using Celery
        # TODO: Switch to API-based email service (Brevo API, SendGrid, etc.) for production
        logger.info(f"Sending mail synchronously for {email} (template: {template_prefix})")
        super().send_mail(template_prefix, email, context)
    
    def _make_context_serializable(self, context):
        """Convert context dict to JSON-safe format by extracting primitive values
        from Django model instances and other non-serializable objects.
        """
        serializable = {}
        for key, value in context.items():
            # Handle Django User model
            if hasattr(value, '_meta') and hasattr(value._meta, 'model_name'):
                # It's a Django model instance - extract key fields
                if value._meta.model_name == 'user':
                    serializable[key] = {
                        'pk': value.pk,
                        'username': getattr(value, 'username', ''),
                        'email': getattr(value, 'email', ''),
                        'first_name': getattr(value, 'first_name', ''),
                        'last_name': getattr(value, 'last_name', ''),
                    }
                else:
                    # Other models - just store the pk
                    serializable[key] = {'pk': value.pk}
            # Handle request objects
            elif hasattr(value, 'META') and hasattr(value, 'method'):
                # It's a request object - extract safe data
                serializable[key] = {
                    'scheme': value.scheme if hasattr(value, 'scheme') else 'http',
                    'method': value.method,
                    'path': value.path,
                }
            # Primitives and simple types
            elif isinstance(value, (str, int, float, bool, type(None), list, dict)):
                serializable[key] = value
            else:
                # For anything else, try to convert to string
                try:
                    serializable[key] = str(value)
                except:
                    # If even str() fails, skip it
                    logger.debug(f"Skipping non-serializable context key: {key}")
                    continue
        
        return serializable
