"""
Production settings for the ecommerce project.
"""
import os
import dj_database_url
from .settings import *

# Security settings
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True
    )
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# HTTPS settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT', 587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')

# PayTM Configuration
PAYTM_MERCHANT_ID = os.environ.get('PAYTM_MERCHANT_ID')
PAYTM_MERCHANT_KEY = os.environ.get('PAYTM_MERCHANT_KEY')
PAYTM_WEBSITE = os.environ.get('PAYTM_WEBSITE', 'DEFAULT')
PAYTM_CHANNEL_ID = os.environ.get('PAYTM_CHANNEL_ID', 'WEB')
PAYTM_INDUSTRY_TYPE_ID = os.environ.get('PAYTM_INDUSTRY_TYPE_ID', 'Retail')
PAYTM_CALLBACK_URL = os.environ.get('PAYTM_CALLBACK_URL', 'https://your-render-url.com/handlerequest/')

# Logging
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
        'level': 'WARNING',
    },
}

# Update the default Django settings for production
CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'https://*.yourdomain.com',
]
