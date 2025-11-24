"""Migration to add PageView model for frontend analytics tracking."""
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_activitylog'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PageView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=1024)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('session_key', models.CharField(blank=True, max_length=128, null=True)),
                ('referrer', models.CharField(blank=True, max_length=1024, null=True)),
                ('ip_address', models.CharField(blank=True, max_length=45, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('duration', models.FloatField(blank=True, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-timestamp'], 'verbose_name': 'Page View', 'verbose_name_plural': 'Page Views'},
        ),
    ]
