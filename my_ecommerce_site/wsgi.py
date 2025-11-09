"""
WSGI config for my_ecommerce_site project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from pathlib import Path

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_ecommerce_site.settings')

# Emergency maintenance wrapper:
# If a file named `.MAINTENANCE` exists in the repository root, the WSGI
# app will return a simple 503 maintenance response for all requests.
# This makes it easy to deploy a tiny emergency change without touching
# templates or app code that may fail at import/render time.

def _make_maintenance_app():
	def app(environ, start_response):
		status = '503 Service Unavailable'
		headers = [('Content-Type', 'text/html; charset=utf-8')]
		start_response(status, headers)
		body = b"<html><body><h1>Site temporarily unavailable</h1><p>We're applying emergency maintenance. Please try again shortly.</p></body></html>"
		return [body]
	return app


_project_root = Path(__file__).resolve().parents[1]
maintenance_marker = _project_root / '.MAINTENANCE'

if maintenance_marker.exists():
	# Return a tiny maintenance WSGI app immediately — avoids template parsing entirely.
	application = _make_maintenance_app()
else:
	application = get_wsgi_application()
