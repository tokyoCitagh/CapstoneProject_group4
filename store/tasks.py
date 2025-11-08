from __future__ import annotations
from celery import shared_task

from allauth.account.adapter import DefaultAccountAdapter


@shared_task(bind=True)
def send_mail_task(self, template_prefix: str, email: str, context: dict) -> None:
    """Background task that uses the default allauth adapter to send email.

    We call DefaultAccountAdapter().send_mail() directly so we don't trigger
    the Celery adapter again (avoids infinite loop).
    """
    try:
        DefaultAccountAdapter().send_mail(template_prefix, email, context)
    except Exception as exc:
        # Failures are logged by the worker; do not re-raise to avoid retries
        # if you prefer retries remove the except or re-raise.
        print(f"send_mail_task failed: {exc}")
