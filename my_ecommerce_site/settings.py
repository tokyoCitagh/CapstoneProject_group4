from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-your-secret-key'
DEBUG = True
ALLOWED_HOSTS = []

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

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'my_ecommerce_site.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation (omitted for brevity)
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
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =============================================================
# CUSTOM AUTHENTICATION AND EMAIL SETTINGS
# =============================================================

# Define the global LOGIN_URL for Django's core login_required decorator
# This points to your namespaced portal login path
LOGIN_URL = '/portal/login/'

# CUSTOMER LOGIN REDIRECT: Redirects all standard logins to the shop (Correctly namespaced)
LOGIN_REDIRECT_URL = 'store:store' 

# GLOBAL LOGOUT REDIRECT: Explicitly use the 'account' namespace for consistency.
# Note: allauth uses 'account_login' as the name.
LOGOUT_REDIRECT_URL = 'account:account_login' 

# --- DJANGO-ALLAUTH CONFIGURATION ---
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

ACCOUNT_EMAIL_VERIFICATION = 'optional' 
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_LOGIN_METHODS = ['username', 'email'] 
ACCOUNT_SIGNUP_FIELDS = ['username', 'email', 'password1', 'password2'] 
ACCOUNT_USERNAME_REQUIRED = True
# =============================================================

# --- EMAIL BACKEND CONFIGURATION (omitted for brevity) ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' 
EMAIL_HOST = 'smtp-relay.brevo.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = '9a9be6001@smtp-brevo.com' 
EMAIL_HOST_PASSWORD = 'xsmtpsib-e80ab4f2092299e803cd9489aa33fd45c81da843439a39b489d63338eecef8f-F3fHUU29SlGJO0XL' 
DEFAULT_FROM_EMAIL = 'maternalandchildrenh@gmail.com'
SERVER_EMAIL = DEFAULT_FROM_EMAIL