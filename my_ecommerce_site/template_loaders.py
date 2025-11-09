import re
from django.conf import settings
from django.template.loaders.filesystem import Loader as FilesystemLoader
from django.template.loaders.app_directories import Loader as AppDirectoriesLoader

_DEFAULT_STATIC_RE = re.compile(
    r"default\s*:\s*static\(\s*(['\"])(?P<path>[^'\"]+)\1\s*\)",
    flags=re.IGNORECASE | re.MULTILINE,
)

def _replace_default_static(source: str) -> str:
    """Replace occurrences of default:static('path') with a literal string
    default:"<STATIC_URL>path" so the template parser doesn't try to call
    the static tag inside a filter expression.
    """
    static_url = getattr(settings, 'STATIC_URL', '/static/') or '/static/'
    if not static_url.endswith('/'):
        static_url = static_url + '/'

    def _repl(m):
        path = m.group('path')
        # ensure no leading slash duplication
        if path.startswith('/'):
            path = path.lstrip('/')
        return f'default:"{static_url}{path}"'

    return _DEFAULT_STATIC_RE.sub(_repl, source)


class PreprocessingFilesystemLoader(FilesystemLoader):
    """Filesystem loader that preprocesses template source before parsing."""

    def get_contents(self, origin):
        source = super().get_contents(origin)
        try:
            return _replace_default_static(source)
        except Exception:
            # On any failure, return original source so we don't mask other errors
            return source


class PreprocessingAppDirectoriesLoader(AppDirectoriesLoader):
    """App directories loader that preprocesses template source before parsing."""

    def get_contents(self, origin):
        source = super().get_contents(origin)
        try:
            return _replace_default_static(source)
        except Exception:
            return source
