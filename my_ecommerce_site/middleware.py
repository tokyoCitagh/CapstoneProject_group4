import logging
import traceback

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
            # Re-raise to let the normal error handlers run (and return 500 to the client)
            raise
