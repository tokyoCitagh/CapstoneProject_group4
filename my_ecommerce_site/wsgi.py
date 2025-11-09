"""
WSGI config for my_ecommerce_site project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

"""WSGI entrypoint.

Temporary emergency: replace the Django WSGI app with a minimal
maintenance WSGI app so the platform can serve a simple 503 response
without importing Django or compiling any templates. Remove this file
or revert after the real fix is deployed.
"""

def application(environ, start_response):
	start_response('503 Service Unavailable', [('Content-Type', 'text/html; charset=utf-8')])
	return [b"Service temporarily unavailable (maintenance)\n"]
