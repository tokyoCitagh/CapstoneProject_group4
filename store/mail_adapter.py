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
        # Defer to a Celery task if the broker is configured
        try:
            if getattr(settings, 'CELERY_BROKER_URL', None):
                # Import here to avoid import-time dependency when Celery not used
                from .tasks import send_mail_task

                # Serialize context to make it JSON-safe for Celery
                # Extract only the data needed for email templates
                serializable_context = self._make_context_serializable(context)

                # enqueue background task
                logger.info(f"Enqueueing mail task for {email} (template: {template_prefix})")
                send_mail_task.apply_async(
                    args=[template_prefix, email, serializable_context],
                    queue='default'
                )
                logger.info(f"Mail task enqueued successfully for {email}")
                return
        except Exception as e:
            # If anything goes wrong, fall back to default behaviour
            logger.warning(f"Failed to enqueue mail task: {type(e).__name__}: {e}. Falling back to synchronous send.")

        # Default synchronous send
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
