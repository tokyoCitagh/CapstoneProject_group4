from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0013_remove_pageview_store_pv_session_key_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='phone',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='shippingaddress',
            name='phone',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
    ]
