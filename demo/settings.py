"""
Django settings for demo project.

Generated by 'django-admin startproject' using Django 2.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = str(os.environ.get('DEBUG')) == "1"

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '.ondigitalocean.app']
if not DEBUG:
    ALLOWED_HOSTS += [os.environ.get("DJANGO_ALLOWED_HOST"), 'sheltercenter.dog']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',
    'schedule_template.apps.ScheduleTemplateConfig',
    'appt_calendar.apps.ApptCalendarConfig',
    'adopter.apps.AdopterConfig',
    'email_mgr.apps.EmailMgrConfig',
    'tinymce',
    'django_summernote',
    'ckeditor'
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

ROOT_URLCONF = 'demo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
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

WSGI_APPLICATION = 'demo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'DISABLE_SERVER_SIDE_CURSORS': True,
    }
}

POSTGRES_DB = os.environ.get("POSTGRES_DB") #database name
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD") #user password
POSTGRES_USER = os.environ.get("POSTGRES_USER") #username
POSTGRES_HOST = os.environ.get("POSTGRES_HOST") #databasehost
POSTGRES_PORT = os.environ.get("POSTGRES_PORT") #databaseport

POSTGRES_READY = (
    POSTGRES_DB is not None
    and POSTGRES_PASSWORD is not None
    and POSTGRES_USER is not None
    and POSTGRES_HOST is not None
    and POSTGRES_PORT is not None
)

if POSTGRES_READY:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": POSTGRES_DB,
            "USER": POSTGRES_USER,
            "PASSWORD": POSTGRES_PASSWORD,
            "HOST": POSTGRES_HOST,
            "PORT": POSTGRES_PORT,
            "DISABLE_SERVER_SIDE_CURSORS": True, #databaseport
        }
    }

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'US/Eastern'

USE_I18N = False

USE_L10N = False

# is_windows = os.environ.get('WINDOWS')
#
# if is_windows:
#     TIME_INPUT_FORMATS = [
#         '%#I:%M %p',
#         '%#I:%M%p',
#         '%#I %p',
#         '%#I%p',
#         '%#H:%M %p',
#         '%#H:%M%p',
#         '%#H %p',
#         '%#H%p',
#     ]
# else:
#     TIME_INPUT_FORMATS = [
#         '%-I:%M %p',
#         '%-I:%M%p',
#         '%-I %p',
#         '%-I%p',
#         '%-H:%M %p',
#         '%-H:%M%p',
#         '%-H %p',
#         '%#H%p',
#     ]


USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') #in prod we want cdn

from .cdn.conf import * # noqa

# if not DEBUG:
#     STATIC_ROOT = ''
#


# https://sheltercenter-demo.nyc3.digitaloceanspaces.com/

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

MEDIA_URL = '/media/'

X_FRAME_OPTIONS = 'SAMEORIGIN'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
#
# TINYMCE_JS_URL = STATIC_URL + 'js/tiny_mce/tiny_mce.js'
# TINYMCE_JS_ROOT = STATIC_ROOT + 'js/tiny_mce'
#
# TINYMCE_JS_URL = os.path.join(MEDIA_ROOT, "js/tiny_mce/tiny_mce.js")
# TINYMCE_JS_ROOT = os.path.join(MEDIA_ROOT, "js/tiny_mce")
TINYMCE_DEFAULT_CONFIG = {
    'plugins': "table,spellchecker,paste,searchreplace",
    'theme': "advanced",
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 100,
    # 'height': 600,
}
# TINYMCE_SPELLCHECKER = True
# TINYMCE_COMPRESSOR = True
