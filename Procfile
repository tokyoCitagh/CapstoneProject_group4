web: gunicorn my_ecommerce_site.wsgi --log-file - --log-level info
worker: celery -A my_ecommerce_site worker --loglevel=info -Q default
