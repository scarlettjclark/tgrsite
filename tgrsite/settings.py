"""
Django settings for tgrsite project.

Generated by 'django-admin startproject' using Django 1.10.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

import django.contrib.messages.constants as message_constants

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from django.urls import reverse_lazy

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ADMINS = [('Webadmin', 'webadmin@warwicktabletop.co.uk')]
MANAGERS = [('Webadmin', 'webadmin@warwicktabletop.co.uk')]
LOGIN_URL = '/login/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
EMAIL_PORT = os.environ.get('EMAIL_PORT', 587)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL = os.environ.get('FROM_EMAIL', 'webmaster@localhost')

s = ''
try:
    from .keys import secret

    s = secret()
except:
    # this will throw a KeyError and crash if neither are specified
    # which is a decent enough way of enforcing it
    s = os.environ['SECRET_KEY']
SECRET_KEY = s

# Defaults off unless explicitly stated in environment variable
try:
    if os.environ['DEBUG'].lower() == 'true':
        DEBUG = True
    else:
        DEBUG = False
except KeyError:
    DEBUG = False

# needs 127 to work on my machine...
ALLOWED_HOSTS = [os.environ.get('HOST', 'localhost'), '127.0.0.1']
PRIMARY_HOST = '127.0.0.1'

if DEBUG:
    from .ipnetworks import IpNetworks
    INTERNAL_IPS = IpNetworks(['127.0.0.1', '192.168.0.0/255.255.0.0'])
else:
    INTERNAL_IPS = ['127.0.0.1']

INSTALLED_APPS = [
    'website_settings',
    'navbar',
    'assets',
    'minutes',
    'inventory',
    'forum',
    'users',
    'rpgs',
    'exec',
    'templatetags',
    'timetable',
    'messaging',
    'gallery',
    'pages',
    'newsletters',
    'notifications',
    'crispy_forms',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tgrsite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'tgrsite/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'tgrsite.context_processors.latestposts',
                'tgrsite.context_processors.mergednavbar'
            ],
        },
    },
]

WSGI_APPLICATION = 'tgrsite.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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

AUTHENTICATION_BACKENDS = [
    'users.backends.CaseInsensitiveModelBackend',
    # 'django.contrib.auth.backends.ModelBackend',
]

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-gb'

USE_I18N = True

USE_L10N = True

# Europe/London means GMT+0 with a DST offset of +1:00 i.e. England time
TIME_ZONE = 'Europe/London'
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
# site URL that static files are served from
STATIC_URL = '/static/'

LOGIN_REDIRECT_URL=reverse_lazy("homepage")

# directories to collect static files from
STATICFILES_DIRS = [
    # where the static files are stored in the repo and collected from
    os.path.join(BASE_DIR, 'static_resources'),
]

# directory the static files are served from
STATIC_ROOT = os.path.join(BASE_DIR, 'STATIC')

# directories for the uploaded files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'MEDIA')

# Monday
FIRST_DAY_OF_WEEK = 1

# Setup Cripsy to render forms bootstrap4ish
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# as advised by python manage.py check --deploy
# prevent browsers from MIME type sniffing. doesn't play nice
# SECURE_CONTENT_TYPE_NOSNIFF=True

# enable browsers' XSS filters
SECURE_BROWSER_XSS_FILTER = True

# ensure all traffic is SSL (https)
SECURE_SSL_REDIRECT = not DEBUG
# session cookies secure-only
SESSION_COOKIE_SECURE = not DEBUG
# same for CSRF cookie
CSRF_COOKIE_SECURE = not DEBUG
# CSRF_COOKIE_HTTPONLY=True
X_FRAME_OPTIONS = 'DENY'

MESSAGE_TAGS = {
    message_constants.DEBUG: 'alert-dark',
    message_constants.INFO: 'alert-primary',
    message_constants.SUCCESS: 'alert-success',
    message_constants.WARNING: 'alert-warning',
    message_constants.ERROR: 'alert-danger',
}

# Allow local configuration (change deploy options etc.)
try:
    from .local_config import *
except ImportError:
    pass
