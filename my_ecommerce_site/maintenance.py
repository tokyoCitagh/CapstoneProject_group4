from django.http import HttpResponse


class MaintenanceMiddleware:
    """Emergency middleware to short-circuit requests with a maintenance page.

    This middleware intentionally returns a simple 503 response for all
    requests. It's intended as a short-term emergency fix to bring the
    service back up without rendering templates (which currently raise a
    TemplateSyntaxError during template compilation).

    IMPORTANT: Remove this middleware after the real fix is deployed and
    verified, or gate it behind an environment flag if you prefer.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return HttpResponse("Service temporarily unavailable (maintenance)", status=503)
