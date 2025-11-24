"""Merge migration to resolve duplicate PageView migration heads."""
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0006_add_pageview"),
        ("store", "0010_add_pageview"),
    ]

    operations = []
