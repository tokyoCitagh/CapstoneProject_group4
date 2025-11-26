from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.sessions.models import Session
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Clear expired sessions and report counts. Intended to be run periodically (cron or scheduler).'

    def handle(self, *args, **options):
        before = Session.objects.count()
        expired = Session.objects.filter(expire_date__lt=timezone.now()).count()
        logger.info(f'cleanup_sessions: total_before={before} expired={expired}')
        # Use built-in clearsessions to respect configured session engine
        call_command('clearsessions')
        after = Session.objects.count()
        logger.info(f'cleanup_sessions: total_after={after}')
        self.stdout.write(self.style.SUCCESS(f'Sessions before: {before}, expired: {expired}, after: {after}'))
