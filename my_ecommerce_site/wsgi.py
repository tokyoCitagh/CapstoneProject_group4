"""
WSGI config for my_ecommerce_site project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Diagnostic startup scan: log any templates containing the vulnerable
# pattern `STATIC_CLOUDINARY_*|default:static('...')` so production logs
# show which template still contains the problematic expression.
try:
	import re
	from pathlib import Path
	BASE_DIR = Path(__file__).resolve().parent.parent
	TEMPLATE_DIRS = [BASE_DIR / 'templates']
	# Also include app template directories if present
	for app_dir in (BASE_DIR / 'store', BASE_DIR / 'services'):
		tdir = app_dir / 'templates'
		if tdir.exists():
			TEMPLATE_DIRS.append(tdir)

	pattern = re.compile(r"STATIC_CLOUDINARY_[A-Z0-9_]+\s*\|\s*default\s*:\s*static\(", re.IGNORECASE)
	found = []
	for tdir in TEMPLATE_DIRS:
		for p in tdir.rglob('*.html'):
			try:
				text = p.read_text(encoding='utf-8')
			except Exception:
				continue
			if pattern.search(text):
				# record first matching line for context
				for i, line in enumerate(text.splitlines(), start=1):
					if pattern.search(line):
						found.append(f"{p}:{i}: {line.strip()}")
						break
	if found:
		print("[TEMPLATE DIAGNOSTIC] Found risky default:static usages:")
		for f in found:
			print("[TEMPLATE DIAGNOSTIC] ", f)
except Exception:
	# Never fail startup because of diagnostics
	pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_ecommerce_site.settings')

application = get_wsgi_application()
