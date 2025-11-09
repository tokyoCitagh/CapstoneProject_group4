"""
WSGI config for my_ecommerce_site project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_ecommerce_site.settings')

# Optionally run collectstatic at startup into a writable directory (e.g. /tmp)
# when FORCE_COLLECTSTATIC_AT_STARTUP=true is set in the environment. This is
# a fallback for platforms where build-time collectstatic didn't run. The
# call is safe and failures are caught so the app still starts.
if os.environ.get('FORCE_COLLECTSTATIC_AT_STARTUP', '').lower() in ('1', 'true', 'yes'):
	try:
		import django
		django.setup()
		from django.core.management import call_command
		# Quiet collectstatic; do not fail startup if it errors
		call_command('collectstatic', '--noinput', verbosity=0)
	except Exception as exc:  # pragma: no cover - runtime guard
		import sys
		print(f"collectstatic at startup failed: {exc}", file=sys.stderr)

application = get_wsgi_application()
