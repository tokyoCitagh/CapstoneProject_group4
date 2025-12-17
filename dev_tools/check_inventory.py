import os
import sys
# Ensure project root is on PYTHONPATH so Django settings can be imported
proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if proj_root not in sys.path:
    sys.path.insert(0, proj_root)
# Ensure Django settings load in development mode so DEFAULT_FROM_EMAIL fallback applies
# This mirrors running with DEBUG=1 (allows a safe DEFAULT_FROM_EMAIL in settings)
os.environ.setdefault('DEBUG', '1')
os.environ.setdefault('DJANGO_SETTINGS_MODULE','my_ecommerce_site.settings')
# Ensure the test client host is allowed by settings (Django test client uses 'testserver')
os.environ.setdefault('ALLOWED_HOSTS', 'testserver')
import django
django.setup()
from django.contrib.auth import get_user_model
User=get_user_model()
username='dev_copilot'
password='DevCopilot!23'
user,created=User.objects.get_or_create(username=username)
if created:
    user.set_password(password)
    user.is_staff=True
    user.is_superuser=True
    user.save()
else:
    user.is_staff=True
    user.is_superuser=True
    user.set_password(password)
    user.save()
from django.test import Client
c=Client()
logged=c.login(username=username,password=password)
print('logged_in=',logged)
r=c.get('/portal/dashboard/inventory/')
print('status=',r.status_code)
ct=r.content.decode('utf-8',errors='replace')
with open('tmp_inventory_out.html','w',encoding='utf-8') as f:
    f.write(ct)
print('\n--- HTML SNIPPET START ---\n')
print(ct[:5000])
print('\n--- HTML SNIPPET END ---\n')
print('Saved full HTML to tmp_inventory_out.html')

# Attempt to fetch an edit page for the first product (if any)
try:
    from store.models import Product
    prod = Product.objects.first()
    if prod:
        pk = prod.pk
        print('Fetching edit page for product pk=', pk)
        er = c.get(f'/portal/products/edit/{pk}/')
        print('edit status=', er.status_code)
        ect = er.content.decode('utf-8', errors='replace')
        with open('tmp_edit_out.html','w',encoding='utf-8') as f:
            f.write(ect)
        print('\n--- EDIT HTML SNIPPET START ---\n')
        print(ect[:5000])
        print('\n--- EDIT HTML SNIPPET END ---\n')
        print('Saved full edit HTML to tmp_edit_out.html')
    else:
        print('No Product found in database; skipping edit page fetch')
except Exception as e:
    print('Failed to fetch edit page:', e)
