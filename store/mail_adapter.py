from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings


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
                send_mail_task.delay(template_prefix, email, context)
                return
        except Exception:
            # If anything goes wrong, fall back to default behaviour
            pass

        # Default synchronous send
        super().send_mail(template_prefix, email, context)
