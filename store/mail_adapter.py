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

                # enqueue background task
                logger.info(f"Enqueueing mail task for {email} (template: {template_prefix})")
                send_mail_task.delay(template_prefix, email, context)
                logger.info(f"Mail task enqueued successfully for {email}")
                return
        except Exception as e:
            # If anything goes wrong, fall back to default behaviour
            logger.warning(f"Failed to enqueue mail task: {type(e).__name__}: {e}. Falling back to synchronous send.")

        # Default synchronous send
        logger.info(f"Sending mail synchronously for {email} (template: {template_prefix})")
        super().send_mail(template_prefix, email, context)
