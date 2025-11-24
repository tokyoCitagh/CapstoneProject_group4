"""Add indexes for PageView to improve analytics queries.

Indexes added:
- session_key: speeds up per-session queries (exit page calculation)
- timestamp: speeds up ordering by timestamp
- path: speeds up grouping/counting by path
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0011_merge_pageview"),
    ]

    operations = [
        migrations.AddIndex(
            model_name='pageview',
            index=models.Index(fields=['session_key'], name='store_pv_session_key_idx'),
        ),
        migrations.AddIndex(
            model_name='pageview',
            index=models.Index(fields=['timestamp'], name='store_pv_timestamp_idx'),
        ),
        migrations.AddIndex(
            model_name='pageview',
            index=models.Index(fields=['path'], name='store_pv_path_idx'),
        ),
    ]
