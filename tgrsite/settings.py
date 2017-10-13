"""
Django settings for tgrsite project.

Generated by 'django-admin startproject' using Django 1.10.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# TODO: find a way to keep this up to date with webadmin address.
# some sort of admin page?
ADMINS=  [('Webadmin', 'ash@sent.com')]
MANAGERS=[('Webadmin', 'ash@sent.com')]
LOGIN_URL='/login/'

EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
EMAIL_PORT = os.environ.get('EMAIL_PORT', 587)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS=True

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
    if os.environ['DEBUG'] == 'True':
        DEBUG = True
    else:
        DEBUG = False
except KeyError:
    DEBUG = False

ALLOWED_HOSTS = [os.environ.get('HOST', 'localhost')]

# Application definition

INSTALLED_APPS = [
    'forum.apps.ForumConfig',
    'users.apps.UsersConfig',
    'rpgs.apps.RpgsConfig',
    'statics.apps.StaticsConfig',
    'exec.apps.ExecConfig',
    'templatetags.apps.TemplatetagsConfig',
    'messaging.apps.MessagingConfig',
    'bugreports.apps.BugreportsConfig',
    'gallery.apps.GalleryConfig',
    'pages.apps.PagesConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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
            ],
        },
    },
]

WSGI_APPLICATION = 'tgrsite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases
# TODO: remove sqlite3
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

AUTHENTICATION_BACKENDS = (
    'users.backends.CaseInsensitiveModelBackend',
)


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-gb'

USE_I18N = True

USE_L10N = True

# https://docs.djangoproject.com/en/1.10/topics/i18n/timezones/
# Notable excerpts:
"""Even if your website is available in only one time zone, it's still good
practice to store data in UTC in your database. The main reason is Daylight
Saving Time (DST). Many countries have a system of DST, where clocks are moved
forward in spring and backward in autumn. If you're working in local time,
you're likely to encounter errors twice a year, when the transitions happen. (
The pytz documentation discusses these issues in greater detail.) This
probably doesn't matter for your blog, but it's a problem if you over-bill or
under-bill your customers by one hour, twice a year, every year. The solution
to this problem is to use UTC in the code and use local time only when
interacting with end users."""

"""When time zone support is enabled (USE_TZ=True), Django uses
time-zone-aware datetime objects. If your code creates datetime objects, they
should be aware too. In this mode, the example above becomes:

from django.utils import timezone

now = timezone.now()
"""

# Europe/London means GMT+0 with a DST offset of +1:00 i.e. England time
TIME_ZONE = 'Europe/London'
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
# site URL that static files are served from
STATIC_URL = '/static/'

# directories to collect static files from
STATICFILES_DIRS = (
    # where the static files are stored in the repo and collected from
    os.path.join(BASE_DIR, 'static_resources'),
 )

# directory the static files are served from
STATIC_ROOT=os.path.join(BASE_DIR, 'STATIC')

# Monday
FIRST_DAY_OF_WEEK=1

# as advised by python manage.py check --deploy
# prevent browsers from MIME type sniffing. doesn't play nice
# SECURE_CONTENT_TYPE_NOSNIFF=True

# enable browsers' XSS filters
SECURE_BROWSER_XSS_FILTER=True

# DEPLOY: Maybe turn some of these on, notably SECURE_SSL_REDIRECT

# ensure all traffic is SSL (https)
# SECURE_SSL_REDIRECT=True
# session cookies secure-only
# SESSION_COOKIE_SECURE=True
# same for CSRF cookie
# CSRF_COOKIE_SECURE=True
# CSRF_COOKIE_HTTPONLY=True
X_FRAME_OPTIONS='DENY'
