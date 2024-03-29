"""
Django settings for transcendence project.

Generated by 'django-admin startproject' using Django 4.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-07cym*_bkdj0xcofg@!golagfl%t!xic_7gbkxyrervni=+v_x'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'sslserver',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api',
    'blockchain',
    'users',
    'games',
    'tournaments',
    'matchmaking',
    'smtp',
    'rest_framework',
    # 'channels',
	
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'users.views.aouth.AouthRequiredMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'api', 'templates'),  # Add the directory path here
        ],
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
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'ft_transcendence_database'),
        'USER': os.environ.get('DB_USER', 'mehdi'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'melody'),
        'HOST': os.environ.get('DB_HOST', 'ft_transcendence_database'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',  # Increase Django's log level to reduce verbosity
            'propagate': False,  # Prevents double logging in console
        },
        'django.db.backends': {
            'level': 'INFO',  # Reduce the output of database-related logs
            'handlers': ['console'],
            'propagate': False,
        },
        'users': {  # Your app
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'api': {  # Your app
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'smtp': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'matchmaking': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'games': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

AUTHENTICATION_BACKENDS = [
    'users.views.aouth.AouthUser',
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_USER_MODEL = 'users.User'

SESSION_COOKIE_SECURE = True 
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_SSL_REDIRECT = True

MEDIA_URL = '/users/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MIDDLEWARE_EXEMPT_URLS = [
    '/admin/',
    '/api/register/',
    '/api/login/',
    '/api/accueil/',
    '/api/twofactor/',
    '/users/aouth_register_form/',
    '/users/aouth_login_form/',
    '/users/aouth_callback_login/',
    '/users/aouth_callback_register/',
    '/smtp/twofactor_oauth/',
]

# 42 OAUTH REGISTRATION
# ---------------------

OAUTH_REGISTER_CLIENT_ID = 'u-s4t2ud-b3c3aab2fe7f2180e74044806b9cbae551124bde9e7364970c26bf3810041aab'
OAUTH_REGISTER_CLIENT_SECRET = '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'
OAUTH_REGISTER_REDIRECT_URI = 'https://localhost:8080/users/aouth_callback_register'

# 42 OAUTH LOGIN
# --------------

AOUTH_LOGIN_CLIENT_ID = 'u-s4t2ud-6e9fbb1976d031cd23a0474ef53b45b8a5912e8bd44198d1393b3ca454785709'
OAUTH_LOGIN_CLIENT_SECRET = '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'
AOUTH_LOGIN_REDIRECT_URI = 'https://localhost:8080/users/aouth_callback_login'

# ASGI_APPLICATION = 'matchmaking.routing.application'

# AUTO_LOGOUT_TIME = 1800
