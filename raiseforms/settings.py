"""
Django settings for raiseforms project.

Generated by 'django-admin startproject' using Django 1.9.8.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

from __future__ import absolute_import
import os
import sys
import dj_database_url
from django.contrib.messages import constants as messages
from celery.schedules import crontab
from forms.tasks import task_download_documents

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'yae54b*++rm5jq@wuo%8)owt(bunexph@&03w=242s8%k$urag'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'forms',
    'anymail',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'raiseforms.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

WSGI_APPLICATION = 'raiseforms.wsgi.application'


# Authentication
AUTH_USER_MODEL = 'forms.AbstractUserModel'

# Tags
MESSAGE_TAGS = {
    messages.ERROR: 'danger'
}

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases


DATABASE_URL = "mysql://bd647441445c99:384c543f@us-cdbr-iron-east-04.cleardb.net/heroku_c55f0079fb2fadf"


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'raiseforms',
        'USER': 'raise',
        'PASSWORD': 'bT7B2nZEjF6G88yR',
        'HOST': 'localhost',
        'PORT': '',
    }
}


DATABASES['default'] = dj_database_url.config(default=DATABASE_URL, conn_max_age=500)


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, "static")
]

STATIC_ROOT = os.path.join(PROJECT_ROOT, "staticfiles")

# Hellosign config
HELLOSIGN_API_KEY = "1955fc7886b608d52e2351ddee5c8ac327eb8eee89c6aa6f7fc10a0ddc347210"
TEMPLATE_IDS = {
    "NDA": "f5adc3e183b9f8ea849a5193143c3f263bc2cc15"
}
CLIENT_ID = "994aa15e2cd50a8d0f7eb56f229271c2"

SITE_ID=1

# MailGun config - Change once custom domain is setup - using django-anymail
ANYMAIL = {
    "MAILGUN_API_KEY": os.environ['MAILGUN_API_KEY'],
    "MAILGUN_SENDER_DOMAIN": os.environ['MAILGUN_DOMAIN'],
}
EMAIL_BACKEND = "anymail.backends.mailgun.MailgunBackend"
DEFAULT_FROM_EMAIL = "Raise Forms Mailer <admin@raiseforms.com>"
# Try nicer looking email address.

# CELERY STUFF
CELERYBEAT_SCHEDULE = {
    'download-every-15-minutes': {
        'task': 'task-download-documents',
        'schedule': crontab(minute='*/1'),
        'args': (HELLOSIGN_API_KEY, AUTH_USER_MODEL),
    },
}
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
