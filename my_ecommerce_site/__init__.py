try:
	# Importing the Celery app can fail in local/dev environments where
	# Celery isn't installed. Wrap in a permissive try/except so management
	# commands (like reupload_media) can run safely without requiring Celery.
	from .celery import app as celery_app
except Exception:
	celery_app = None

__all__ = ('celery_app',)
