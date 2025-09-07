"""
WSGI config for ecommerce project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Use production settings in production environment
if os.environ.get('RENDER', '').lower() == 'true':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.production_settings')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')

application = get_wsgi_application()
