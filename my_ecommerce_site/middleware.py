import logging
import traceback
import sys

logger = logging.getLogger(__name__)


class ExceptionLoggingMiddleware:
    """Middleware that logs uncaught exceptions with full traceback to the default logger.

    This is intended as a temporary diagnostic aid in production to ensure exceptions
    are visible in container logs (stdout/stderr). It re-raises the exception after
    logging so normal error handling still occurs.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception as exc:
            # Log request info and full traceback so the platform logs contain the
            # precise Python exception for debugging.
            try:
                logger.exception("Unhandled exception processing request %s", getattr(request, 'path', '<unknown>'))
            except Exception:
                # If logging itself fails, fallback to printing the traceback.
                print("Exception while logging request:")
                traceback.print_exc()
            # Always print the full traceback to stdout as a fallback so hosting
            # platforms that don't capture logger output still receive it.
            try:
                print("--- START EXCEPTION TRACEBACK (diagnostic) ---")
                traceback.print_exc()
                print("Request path:", getattr(request, 'path', '<unknown>'))
                print("--- END EXCEPTION TRACEBACK (diagnostic) ---")
                sys.stdout.flush()
            except Exception:
                pass
            # Re-raise to let the normal error handlers run (and return 500 to the client)
            raise


class NoCacheHtmlMiddleware:
    """Ensure HTML responses are not aggressively cached by browsers.

    This is a short-lived emergency middleware to force clients (notably
    mobile Safari) to revalidate HTML pages so inline scripts and runtime
    loaders are picked up immediately after deploys.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            content_type = response.get('Content-Type', '')
            if content_type and 'text/html' in content_type.lower():
                # Instruct clients to revalidate HTML pages rather than using a stale cache
                response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
                response['Pragma'] = 'no-cache'
                response['Expires'] = '0'
        except Exception:
            # Fail silently - we don't want middleware to break requests
            pass
        return response
