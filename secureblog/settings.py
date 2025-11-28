"""
Django 5+ Secure Blog Application Settings
OWASP & NIST Compliant Configuration
"""

from pathlib import Path
from decouple import config
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production-12345678901234567890')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    
    # Third-party apps
    'django_otp',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_static',
    'django_ckeditor_5',
    # 'admin_honeypot',  # Commented out - incompatible with Django 5+
    'rest_framework',
    
    # Local apps
    'accounts.apps.AccountsConfig',
    'blog.apps.BlogConfig',
    'security.apps.SecurityConfig',
    'healthcenter.apps.HealthcenterConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'csp.middleware.CSPMiddleware',
    'security.middleware.SecurityHeadersMiddleware',
    'security.middleware.RateLimitMiddleware',
]

ROOT_URLCONF = 'secureblog.urls'

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
            'autoescape': True,
        },
    },
]

WSGI_APPLICATION = 'secureblog.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_AGE = 3600
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript to read CSRF token for AJAX requests like CKEditor uploads
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_USE_SESSIONS = False  # Must be False to allow JavaScript access to CSRF token
CSRF_FAILURE_VIEW = 'security.views.csrf_failure'

CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "https://cdn.ckeditor.com", "https://cdn.jsdelivr.net")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://cdn.ckeditor.com", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com")
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_FONT_SRC = ("'self'", "https://cdn.ckeditor.com", "https://cdnjs.cloudflare.com")
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_SRC = ("'self'", "https://www.google.com", "https://www.openstreetmap.org")  # Allow Google Maps and OpenStreetMap iframe embedding
CSP_FRAME_ANCESTORS = ("'none'",)
CSP_FORM_ACTION = ("'self'",)
CSP_BASE_URI = ("'self'",)

FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880
FILE_UPLOAD_PERMISSIONS = 0o644
ALLOWED_UPLOAD_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.pdf']

RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'security': {
            'handlers': ['file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

os.makedirs(BASE_DIR / 'logs', exist_ok=True)

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                    'bulletedList', 'numberedList', 'blockQuote', 'imageUpload'],
    },
}

CKEDITOR_5_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
CKEDITOR_UPLOAD_PATH = "uploads/"
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Google Maps API Configuration
GOOGLE_MAPS_API_KEY = config('GOOGLE_MAPS_API_KEY', default=None)
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'healthcenter:dashboard'
LOGOUT_REDIRECT_URL = 'accounts:login'

ADMIN_HONEYPOT_EMAIL_ADMINS = True

OTP_TOTP_ISSUER = 'SecureBlog'
OTP_LOGIN_URL = 'accounts:otp_login'

PASSWORD_RESET_TIMEOUT = 3600
