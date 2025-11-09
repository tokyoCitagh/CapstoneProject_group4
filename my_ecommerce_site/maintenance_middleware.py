import os
from django.conf import settings
from django.http import HttpResponse


class MaintenanceMiddleware:
    """Simple maintenance middleware.

    When `settings.MAINTENANCE_MODE` is truthy and DEBUG is False, this
    middleware returns a small 503 HTML response for all requests. This
    is intentionally minimal so deploys with template issues can be
    brought back online quickly. Remove or set `MAINTENANCE_MODE=False`
    in `settings.py` to disable.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            enabled = getattr(settings, 'MAINTENANCE_MODE', False)
        except Exception:
            enabled = False

        # Only serve maintenance when explicitly enabled and not in DEBUG
        if enabled and not getattr(settings, 'DEBUG', False):
            html = (
                '<!doctype html>'
                '<html><head><meta charset="utf-8"><title>Maintenance</title></head>'
                '<body style="font-family: system-ui, -apple-system, Roboto, sans-serif; padding:2rem; text-align:center">'
                '<h1>Service temporarily unavailable</h1>'
                '<p>We&apos;re performing maintenance and will be back shortly.</p>'
                '</body></html>'
            )
            return HttpResponse(html, content_type='text/html', status=503)

        return self.get_response(request)
