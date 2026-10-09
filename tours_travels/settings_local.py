"""
Local development settings for Natures Gift Expeditions.

This module is intentionally separate from production settings so local work can
use SQLite without changing the Render configuration.
"""

import os

os.environ['DJANGO_ENV'] = 'local'

from .settings import *

DEBUG = True
DJANGO_ENV = 'development'
SECRET_KEY = 'django-insecure-natures-gift-local-development-key'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'natures_gift_local.sqlite3',
    }
}

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_PROVIDER = 'django'
SITE_URL = 'http://127.0.0.1:8021'
DEFAULT_FROM_EMAIL = 'Natures Gift Expeditions <info@example.com>'
ADMIN_EMAIL = 'info@example.com'
JOBS_EMAIL = 'careers@example.com'
NEWSLETTER_EMAIL = 'marketing@example.com'

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
