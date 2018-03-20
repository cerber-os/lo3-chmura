"""
Django settings for lo3 project.

Generated by 'django-admin startproject' using Django 1.11.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('lo3_django_secretkey', '*v^4+%9%0qv0i8mzy5hsz&e9k*%f5*j&(%9)2k-!gw8e195v3c')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('lo3_django_debug', 'True') == 'True'

if not DEBUG:
    ALLOWED_HOSTS = ['localhost', 'cerberos.pl']
else:
    ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'chmura.apps.ChmuraConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_crontab',
    'django_user_agents',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
]

ROOT_URLCONF = 'lo3.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'lo3.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'pl-PL'

TIME_ZONE = 'Europe/Warsaw'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

# Cron jobs (updating timetable, substitution, etc.)
# https://github.com/kraiz/django-crontab

CRONJOBS = [
    ('0 0 */2 * *', 'chmura.timetable.updateTimeTables'),
    # ('0 */12 * * *', 'chmura.news.newsJob'),
    # ('0 0 */10 * *', 'chmura.news.agendaJob'),
    ('0 */1 * * *', 'chmura.subst.updateJob'),
    ('0 12 1 * *', 'chmura.updateids.updateid'),
]

# Connection settings

DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows; U; Win 9x 4.90; de-DE; rv:0.9.2) Gecko/20010726 Netscape7/6.1'
if DEBUG:
    ENABLE_TOR = False
    ENABLE_AGGRESSIVE_IP_CHANGE = False
else:
    ENABLE_TOR = True
    ENABLE_AGGRESSIVE_IP_CHANGE = True

# Securiy

if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_CONTENT_TYPE_NOSNIFF = True


# Logging

LOGGING_LEVEL = 'INFO'
LOGGING_COLORS = True
if not DEBUG:
    LOGGING_LEVEL = 'WARN'
    LOGGING_COLORS = False
    ADMINS = [('Nowy plan lekcji', 'cerber@cerberos.pl')]

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'mail_admins': {
                'level': 'ERROR',
                'class': 'django.utils.log.AdminEmailHandler',
                'include_html': True,
            }
        },
    }

# Cache location
# TODO: Wprowadzić to wszędzie
CACHE_LOCATION = os.path.dirname(os.path.abspath(__file__)) + '/../cache/'
