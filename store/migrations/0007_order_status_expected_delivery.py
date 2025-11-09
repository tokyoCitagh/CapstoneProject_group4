from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0006_shippingaddress_country"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="status",
            field=models.CharField(choices=[('PENDING','Pending'),('PROCESSING','Processing'),('SHIPPED','Shipped'),('COMPLETED','Completed'),('CANCELLED','Cancelled')], default='PENDING', max_length=20),
        ),
        migrations.AddField(
            model_name="order",
            name="expected_delivery",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
