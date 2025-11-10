"""
Management command to update Django site name and domain.
Run: python manage.py update_site --domain yourdomain.com --name "Your Site Name"
"""
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = 'Update Django site name and domain'

    def add_arguments(self, parser):
        parser.add_argument(
            '--domain',
            type=str,
            default='web-production-20e5.up.railway.app',
            help='Site domain (default: web-production-20e5.up.railway.app)',
        )
        parser.add_argument(
            '--name',
            type=str,
            default='Image Electronics',
            help='Site name (default: Image Electronics)',
        )

    def handle(self, *args, **options):
        domain = options['domain']
        name = options['name']
        
        try:
            site = Site.objects.get(id=1)
            site.domain = domain
            site.name = name
            site.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated site:\n  Domain: {domain}\n  Name: {name}')
            )
        except Site.DoesNotExist:
            site = Site.objects.create(id=1, domain=domain, name=name)
            self.stdout.write(
                self.style.SUCCESS(f'Created new site:\n  Domain: {domain}\n  Name: {name}')
            )
