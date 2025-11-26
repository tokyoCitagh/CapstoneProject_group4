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


class EnsureSessionMiddleware:
    """Ensure anonymous HTML GET requests receive a session key.

    This middleware is opt-in via the `SESSION_ENSURE_ENABLED` setting.
    When enabled it will create a lightweight session for anonymous GET
    requests that return HTML so frontend pageview tracking can rely on
    `request.session.session_key` being present for most visitors.

    To avoid unnecessary DB churn this only runs for GET requests, for
    anonymous users, and only when the response Content-Type is HTML.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            from django.conf import settings
            # Honor opt-in flag
            if not getattr(settings, 'SESSION_ENSURE_ENABLED', False):
                return response

            # Only for anonymous GET requests
            if request.method != 'GET':
                return response
            if getattr(request, 'user', None) and request.user.is_authenticated:
                return response

            content_type = response.get('Content-Type', '')
            if not content_type or 'text/html' not in content_type.lower():
                return response

            # If a session key already exists, nothing to do
            try:
                if request.session.session_key:
                    return response
            except Exception:
                # If session object isn't available for some reason, skip
                return response

            # Create a minimal session marker and save to ensure a session_key
            try:
                request.session['anon_session'] = True
                # Use configured cookie age if present
                if hasattr(settings, 'SESSION_COOKIE_AGE'):
                    request.session.set_expiry(settings.SESSION_COOKIE_AGE)
                request.session.save()
                logger.info('EnsureSessionMiddleware: created session for path=%s', getattr(request, 'path', ''))
            except Exception:
                logger.exception('EnsureSessionMiddleware failed to create session')
        except Exception:
            # Don't break requests if middleware fails
            logger.exception('EnsureSessionMiddleware top-level error')

        return response
