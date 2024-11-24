"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 5.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from dotenv import load_dotenv
from os import environ, path
from pathlib import Path

# Loading environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-ds@k8lg73zd8fllp1u%b2^kjcf7yih8dcgoe3y@hmnpz7r=8g%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


SHOPIFY_API_URL = environ.get('SHOPIFY_API_URL')
SHOPIFY_APP_URL = environ.get('SHOPIFY_APP_URL')

ALLOWED_HOSTS = [SHOPIFY_API_URL.replace('https://', '').replace('http://', '')]

# cors settings
CORS_ALLOWED_ORIGINS = [
    SHOPIFY_API_URL, SHOPIFY_APP_URL
]
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = [
    'ngrok-skip-browser-warning',
    'x-shopify-access-token',
    'x-shopify-oauth-state-param',
    'authorization',
]

# csrf settings
CSRF_TRUSTED_ORIGINS = [
    SHOPIFY_API_URL,
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'api',
    'compliance',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

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

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases


USE_AWS_SECRET_MANAGER = False

if USE_AWS_SECRET_MANAGER:
    from .aws_secrets_manager import get_secret
    aws_secret = get_secret()

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': environ.get('DB_NAME'),
            'USER': aws_secret['username'],
            'PASSWORD': aws_secret['password'],
            'HOST': environ.get('DB_HOST'),
            'PORT': environ.get('DB_PORT')
        }
    }

else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': environ.get('POSTGRES_DB'),
            'USER': environ.get('POSTGRES_USER'),
            'PASSWORD': environ.get('POSTGRES_PASSWORD'),
            'HOST': environ.get('POSTGRES_HOST'),
            'PORT': environ.get('POSTGRES_PORT')
        }
    }


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/shopify/static/'
STATIC_ROOT = path.join(BASE_DIR, 'static')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

APPEND_SLASH = False

SHOPIFY_API_KEY = environ.get('SHOPIFY_API_KEY')
SHOPIFY_API_SECRET = environ.get('SHOPIFY_API_SECRET')
SHOPIFY_API_SCOPES = environ.get('SHOPIFY_API_SCOPES')
SHOPIFY_API_VERSION = environ.get('SHOPIFY_API_VERSION', 'unstable')


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} [{levelname}] {name} ({filename}:{lineno}) {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {name} - {message} ({filename}:{lineno})',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': path.join(BASE_DIR, 'django.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'api': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'compliance': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
