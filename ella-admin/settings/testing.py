from .base import *

ENV = 'testing'

SECRET_KEY = '8g#mt#p!f^+xy-n6p+64n&cm92b61zi6_9q097(3e0o)xntbt_'

DEBUG = True

ALLOWED_HOSTS = ['*']

FRONTEND_URL = 'http://localhost'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'password123',
        'HOST': 'postgresql',
        'PORT': '5432',
    }
}

STATIC_URL = 'static/'
MEDIA_URL = f'http://localhost/media/'
MEDIA_ROOT = 'media/'
STATIC_ROOT = 'api/static'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.mailtrap.io'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 2525
EMAIL_SUPPORT_EMAIL = 'ella-support@mail.com'
