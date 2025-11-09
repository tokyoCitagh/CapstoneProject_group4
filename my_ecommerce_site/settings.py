from pathlib import Path
from decouple import config
import dj_database_url
import os
import cloudinary

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- DECOUPLE SETUP FOR .ENV FILE ---
# Quick-start development settings - unsuitable for production
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
# Read ALLOWED_HOSTS from env (comma separated) for production (Railway)
_allowed = config('ALLOWED_HOSTS', default='')
ALLOWED_HOSTS = [h.strip() for h in _allowed.split(',') if h.strip()] if _allowed else []

# Allow configuring CSRF trusted origins via environment (comma-separated list)
# Useful for deployment platforms where you can't edit settings directly.
_csrf = config('CSRF_TRUSTED_ORIGINS', default='')
if _csrf:
    CSRF_TRUSTED_ORIGINS = [u.strip() for u in _csrf.split(',') if u.strip()]

# NOTE: Ensure DEBUG=False in production. DEBUG can be toggled via the DEBUG env var above.

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Third-party apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'widget_tweaks',
    'django.contrib.humanize',

    # My apps
    'store',
    'services',
]

SITE_ID = 1

# Maintenance mode: controlled via environment so we can toggle without
# changing code during production troubleshooting. Default to False.
MAINTENANCE_MODE = config('MAINTENANCE_MODE', default=False, cast=bool)

MIDDLEWARE = [
    'my_ecommerce_site.maintenance_middleware.MaintenanceMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'my_ecommerce_site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        # Disable the cached template loader so deploys pick up template changes
        # immediately. Some platforms or buildpacks wrap loaders with the cached
        # loader in production; explicitly configure loaders to avoid using the
        # cached loader which can serve stale compiled templates after deploys.
        'APP_DIRS': False,
        'OPTIONS': {
            # Use preprocessing loaders to rewrite any occurrences of
            # "default:static('...')" into a safe literal default so bad
            # templates left on the running image don't cause a parse-time
            # TemplateSyntaxError. These loaders delegate to the standard
            # filesystem/app_directories loaders but preprocess the source.
            'loaders': [
                'my_ecommerce_site.template_loaders.PreprocessingFilesystemLoader',
                'my_ecommerce_site.template_loaders.PreprocessingAppDirectoriesLoader',
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Provide safe static/cloudinary URLs so templates avoid
                # calling template tags inside filters (which causes parse
                # errors when written like "...|default:static('...')").
                'store.context_processors.static_cloudinary_urls',
            ],
        },
    },
]

WSGI_APPLICATION = 'my_ecommerce_site.wsgi.application'

# Database: prefer DATABASE_URL (Railway) with fallback to sqlite for local dev
DATABASE_URL = config('DATABASE_URL', default='')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600),
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation (omitted for brevity)
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher', 
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.ScryptPasswordHasher',
]

AUTH_PASSWORD_VALIDATORS = [
    # ... (omitted)
]

# Internationalization (omitted for brevity)
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (omitted for brevity)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
# Where `collectstatic` will collect static files for production
# Allow overriding STATIC_ROOT from environment to handle platform-specific
# container working-dir differences (some deploys use /app as project root).
_static_root_env = os.environ.get('STATIC_ROOT')
# If the deploy needs collectstatic to run at container startup (for
# platforms where build-time collectstatic isn't available), set
# FORCE_COLLECTSTATIC_AT_STARTUP=true and we will collect into a
# writable tmp directory. Otherwise, default to the project `staticfiles`
# directory so collectstatic at build-time (recommended) will populate it.
if os.environ.get('FORCE_COLLECTSTATIC_AT_STARTUP', '').lower() in ('1', 'true', 'yes'):
    # Use a writable tmp dir for runtime collection
    STATIC_ROOT = Path(os.environ.get('STATIC_ROOT', '/tmp/staticfiles'))
elif _static_root_env:
    STATIC_ROOT = Path(_static_root_env)
else:
    STATIC_ROOT = BASE_DIR / 'staticfiles'
# Use WhiteNoise storage backend for compressed static files on Railway
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -------------------------
# Media / External storage
# -------------------------
# We support two external storage options: S3 (django-storages) or Cloudinary.
# Cloudinary is preferred here when `USE_CLOUDINARY=true` in env.
USE_CLOUDINARY = config('USE_CLOUDINARY', default=False, cast=bool)
if USE_CLOUDINARY:
    # Add cloudinary apps if not present
    if 'cloudinary' not in INSTALLED_APPS:
        INSTALLED_APPS.append('cloudinary')
    if 'cloudinary_storage' not in INSTALLED_APPS:
        INSTALLED_APPS.append('cloudinary_storage')

    # Cloudinary can be configured by a single CLOUDINARY_URL env var or by parts
    CLOUDINARY_URL = config('CLOUDINARY_URL', default=None)
    if not CLOUDINARY_URL:
        CLOUDINARY_STORAGE = {
            'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME'),
            'API_KEY': config('CLOUDINARY_API_KEY'),
            'API_SECRET': config('CLOUDINARY_API_SECRET'),
        }
    else:
        # django-cloudinary-storage will pick up CLOUDINARY_URL automatically from env
        CLOUDINARY_STORAGE = {}

    # Ensure the Cloudinary client is configured at runtime from the same env values
    # (python-decouple reads .env but other libs like cloudinary read os.environ or cloudinary.config)
    try:
        if CLOUDINARY_URL:
            cloudinary.config(cloudinary_url=CLOUDINARY_URL)
        else:
            cloudinary.config(
                cloud_name=config('CLOUDINARY_CLOUD_NAME', default=None),
                api_key=config('CLOUDINARY_API_KEY', default=None),
                api_secret=config('CLOUDINARY_API_SECRET', default=None),
            )
    except Exception:
        # Fail softly here; Cloudinary client will raise if used without proper config later
        pass

    # Use Cloudinary for uploaded media
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

    # Optionally use Cloudinary for static files
    if config('USE_CLOUDINARY_FOR_STATIC', default=False, cast=bool):
        STATICFILES_STORAGE = 'cloudinary_storage.storage.StaticHashedCloudinaryStorage'
        # When using Cloudinary for static, you can optionally set a custom domain
        CLOUDINARY_STATIC_URL = config('CLOUDINARY_STATIC_URL', default=None)
        if CLOUDINARY_STATIC_URL:
            STATIC_URL = CLOUDINARY_STATIC_URL
        else:
            # Default STATIC_URL will be provided by the storage backend
            pass
else:
    # Fallback to S3 if configured
    USE_S3 = config('USE_S3', default=False, cast=bool)
    if USE_S3:
        # Add storages app if using S3
        if 'storages' not in INSTALLED_APPS:
            INSTALLED_APPS.append('storages')

        AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
        AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
        AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default=None)
        AWS_S3_CUSTOM_DOMAIN = config('AWS_S3_CUSTOM_DOMAIN', default=None)
        # Recommended: set this to None to rely on bucket permissions
        AWS_DEFAULT_ACL = None
        AWS_S3_OBJECT_PARAMETERS = {
            'CacheControl': 'max-age=86400',
        }

        # Use S3 for uploaded media files
        DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

        # Optionally use S3 for static files as well
        if config('USE_S3_FOR_STATIC', default=False, cast=bool):
            STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
            if AWS_S3_CUSTOM_DOMAIN:
                STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
                MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
            else:
                STATIC_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/static/'
                MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/media/'
        else:
            # Keep WhiteNoise for static, but point media to S3
            if AWS_S3_CUSTOM_DOMAIN:
                MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
            else:
                MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/media/'
    else:
        # Local filesystem for media (development)
        MEDIA_URL = '/media/'
        MEDIA_ROOT = BASE_DIR / 'media'


# =============================================================
# CUSTOM AUTHENTICATION AND EMAIL SETTINGS
# =============================================================

# Session, Login and Authentication Settings
LOGIN_URL = '/accounts/login/' 
LOGIN_REDIRECT_URL = 'store:store' 
LOGOUT_REDIRECT_URL = '/accounts/login/' 
ACCOUNT_LOGOUT_REDIRECT_URL = LOGOUT_REDIRECT_URL 

# Password Reset Configuration
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True  # Automatically log users in after reset
ACCOUNT_PASSWORD_RESET_TOKEN_GENERATOR = 'allauth.account.forms.EmailAwarePasswordResetTokenGenerator'

# --- DJANGO-ALLAUTH CONFIGURATION ---
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Django Allauth Settings
ACCOUNT_LOGIN_METHODS = {'username'}  # Updated from ACCOUNT_AUTHENTICATION_METHOD
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'  # Specify username field
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']  # Updated required fields
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_UNIQUE_EMAIL = True

# Password reset settings
PASSWORD_RESET_TIMEOUT = 3600  # 1 hour in seconds (Django's native setting)
ACCOUNT_PASSWORD_RESET_TIMEOUT = 3600  # 1 hour in seconds (django-allauth setting)

# Enable code-based password reset (new in allauth 65+)
ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED = False  # Use token-based reset instead

# Custom adapter settings
ACCOUNT_ADAPTER = 'allauth.account.adapter.DefaultAccountAdapter'
ACCOUNT_PRESERVE_USERNAME_CASING = False  # Usernames are stored in lowercase

# Password reset URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/store/'

# Rate limiting configuration (new format)
ACCOUNT_RATE_LIMITS = {
    # 5 failed attempts will trigger a 5-minute timeout
    'login_failed': '5/5m'
}

# Use custom login form
ACCOUNT_FORMS = {
    'login': 'store.forms.CustomLoginForm'
}

# Use a custom allauth adapter that enqueues emails to Celery when configured.
ACCOUNT_ADAPTER = config('ACCOUNT_ADAPTER', default='store.mail_adapter.CeleryAccountAdapter')

# Password settings
ACCOUNT_PASSWORD_MIN_LENGTH = 8

ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

# =============================================================

# --- EMAIL BACKEND CONFIGURATION (READING FROM .ENV) ---
# Allow overriding the email backend from environment so we can switch to a
# non-blocking backend (console/dummy) in production for diagnostics.
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')

# Load email settings securely
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')
SERVER_EMAIL = config('SERVER_EMAIL', default=DEFAULT_FROM_EMAIL)

# Celery / Redis configuration (for background tasks)
# Provide REDIS_URL in Railway variables (e.g. redis://:<password>@<host>:<port>/0)
REDIS_URL = config('REDIS_URL', default='')
if REDIS_URL:
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
else:
    # Allow explicit override via CELERY_BROKER_URL env var for local dev
    CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = CELERY_BROKER_URL

# Whether to run Celery tasks eagerly (useful for local dev / debugging)
CELERY_TASK_ALWAYS_EAGER = config('CELERY_TASK_ALWAYS_EAGER', default=False, cast=bool)

# Enable site framework (required for allauth)
SITE_ID = 1
# Ensure the site domain is set correctly in the admin interface

# ----------------------------
# Logging: ensure logs are written to stdout so platform captures them
# ----------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}