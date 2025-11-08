import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_ecommerce_site.settings')

app = Celery('my_ecommerce_site')

# Pull configuration from Django settings with CELERY_ prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in installed apps
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
