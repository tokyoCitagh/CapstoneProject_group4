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
    'django.contrib.humanize',  # Added for intcomma and naturaltime in dashboard

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
        # --- CRITICAL CHANGE: Tell Django to look here first ---
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


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Default primary key field type

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =============================================================
# CUSTOM AUTHENTICATION AND EMAIL SETTINGS
# =============================================================

# FIX: Set the staff dashboard as the login redirect
LOGIN_REDIRECT_URL = 'portal:inventory_dashboard'

# CRITICAL FIX: Set this to the staff login URL name for logout redirect
LOGOUT_REDIRECT_URL = 'portal_login'

# --- DJANGO-ALLAUTH CONFIGURATION ---
AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of allauth settings
    'django.contrib.auth.backends.ModelBackend',
    # allauth specific authentication methods, such as login by email
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Crucial for your requirement: Email is sent, but login is NOT blocked
ACCOUNT_EMAIL_VERIFICATION = 'optional' 
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True

# Allows login using either username or email
ACCOUNT_LOGIN_METHODS = ['username', 'email'] 

# Standard signup fields
ACCOUNT_SIGNUP_FIELDS = ['username', 'email', 'password1', 'password2'] 
ACCOUNT_USERNAME_REQUIRED = True
# =============================================================

# --- EMAIL BACKEND CONFIGURATION (Brevo - REAL EMAIL DELIVERY) ---

# Switched to SMTP Backend for real email delivery via Brevo
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' 

# Brevo SMTP Connection Details (CONFIRMED)
EMAIL_HOST = 'smtp-relay.brevo.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Brevo Credentials (CONFIRMED LOGIN & SMTP KEY)
EMAIL_HOST_USER = '9a9be6001@smtp-brevo.com' 
EMAIL_HOST_PASSWORD = 'xsmtpsib-e80ab4f2092299e803cd9489aa33fd45c81da843439a39b489d63338eecef8f-F3fHUU29SlGJO0XL' 

# Sender Identity (MUST be verified in Brevo)
DEFAULT_FROM_EMAIL = 'maternalandchildrenh@gmail.com'
SERVER_EMAIL = DEFAULT_FROM_EMAIL