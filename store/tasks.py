from __future__ import annotations
from celery import shared_task
from django.contrib.auth import get_user_model

from allauth.account.adapter import DefaultAccountAdapter


@shared_task(bind=True)
def send_mail_task(self, template_prefix: str, email: str, context: dict) -> None:
    """Background task that uses the default allauth adapter to send email.

    We call DefaultAccountAdapter().send_mail() directly so we don't trigger
    the Celery adapter again (avoids infinite loop).
    
    The context has been serialized by CeleryAccountAdapter, so we need to
    reconstruct any model instances before passing to the email renderer.
    """
    try:
        # Reconstruct model instances from serialized context
        reconstructed_context = _reconstruct_context(context)
        DefaultAccountAdapter().send_mail(template_prefix, email, reconstructed_context)
    except Exception as exc:
        # Failures are logged by the worker; do not re-raise to avoid retries
        # if you prefer retries remove the except or re-raise.
        print(f"send_mail_task failed: {exc}")


def _reconstruct_context(context: dict) -> dict:
    """Reconstruct Django model instances from serialized context data."""
    reconstructed = {}
    User = get_user_model()
    
    for key, value in context.items():
        # Check if this looks like a serialized User model
        if isinstance(value, dict) and 'pk' in value and 'username' in value:
            try:
                # Fetch the actual User instance
                user = User.objects.get(pk=value['pk'])
                reconstructed[key] = user
            except User.DoesNotExist:
                # If user was deleted, keep the serialized dict
                reconstructed[key] = value
        else:
            # Everything else passes through unchanged
            reconstructed[key] = value
    
    return reconstructed
