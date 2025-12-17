from django.db import migrations
from django.contrib.sites.models import Site


def update_site(apps, schema_editor):
    """Update the default site to use the production domain"""
    try:
        site = Site.objects.get(id=1)
        site.domain = 'www.imageelectronics.org'
        site.name = 'Image Electronics'
        site.save()
    except Site.DoesNotExist:
        pass


def reverse_site(apps, schema_editor):
    """Revert to default domain"""
    try:
        site = Site.objects.get(id=1)
        site.domain = 'example.com'
        site.name = 'example.com'
        site.save()
    except Site.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_productspecification_specification'),
    ]

    operations = [
        migrations.RunPython(update_site, reverse_site),
    ]
