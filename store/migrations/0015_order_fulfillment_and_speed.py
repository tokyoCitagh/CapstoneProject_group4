from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0014_add_phone_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='fulfillment',
            field=models.CharField(choices=[('delivery', 'Delivery'), ('pickup', 'Pick-up')], default='delivery', max_length=20),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_speed',
            field=models.CharField(choices=[('standard', 'Standard'), ('express', 'Express')], default='standard', max_length=20),
        ),
    ]
