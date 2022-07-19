"""Common Django settings for nourish project."""
from __future__ import annotations

import inspect
from pathlib import Path
from typing import Callable

import django.utils.encoding
import django.utils.translation
from decouple import Csv, config
from django.contrib.messages import constants as messages
from drf_braces import utils

# Django 4.0.1 removed django.utils.encoding.force_text.
# Required by django-bitfield.
django.utils.encoding.force_text = django.utils.encoding.force_str  # type: ignore
# Django 4.0.1 removed django.utils.translation.ugettext_lazy.
# Required by django-bitfield.
django.utils.translation.ugettext_lazy = django.utils.translation.gettext_lazy  # type: ignore
# DRF braces (0.3.4) doesn't read keyword args when computing __init__ field params. Monkey patch the fix.


def find_function_args(func: Callable) -> list[str]:
    """
    Get the list of parameter names which function accepts.
    """
    try:
        spec = inspect.getfullargspec(func)
        arg_list = spec[0]
        if hasattr(spec, "kwonlyargs"):
            arg_list += spec.kwonlyargs
        return [i for i in arg_list if i not in utils.IGNORE_ARGS]
    except TypeError:
        return []


utils.find_function_args = find_function_args

DEBUG = config("DEBUG", default=False, cast=bool)
TEMPLATE_DEBUG = False
SITE_ID = config("SITE_ID", default=1, cast=int)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())
CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", cast=Csv())
MESSAGE_TAGS = {
    messages.DEBUG: "alert-secondary",
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-danger",
}

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_URLCONF = "nourish.urls"

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

WSGI_APPLICATION = "nourish.wsgi.application"
MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
CRISPY_TEMPLATE_PACK = "bootstrap4"

# Application definition
INSTALLED_APPS = [
    "accounts",
    "bitfield",
    "crispy_forms",
    "corsheaders",
    "django_extensions",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.postgres",
    "django.contrib.sitemaps",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "nutrition_tracker.apps.NutritionTrackerConfig",
    "rest_framework",
    "rest_framework_api_key",
    "rest_framework.authtoken",
    "dj_rest_auth",  # after rest_framework apps
    "dj_rest_auth.registration",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",  # needed for dj_rest_auth
    "widget_tweaks",
    "users.apps.UsersConfig",
]

MIGRATION_MODULES = {
    "nutrition_tracker": "nutrition_tracker.database.migrations",
}

# https://docs.djangoproject.com/en/3.2/ref/middleware/#middleware-ordering
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "nutrition_tracker.middleware.timezone.TimezoneMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "nutrition_tracker.context_processors.add_constants",
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
]
# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]
AUTH_USER_MODEL = "users.User"
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_FORMS = {
    "login": "accounts.forms.LoginForm",
    "signup": "accounts.forms.SignupForm",
}
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
# Set default primary key for all models.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_REDIRECT_URL = "index"
LOGOUT_REDIRECT_URL = "index"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = True
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = "noreply@famnom.com"
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_HOST_USER = config("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", "")

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "US/Pacific"
USE_I18N = True
USE_L10N = True
USE_TZ = True
DATE_FORMAT = "N j, Y"
DATETIME_FORMAT = "N j, Y, P"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/
STATIC_ROOT = BASE_DIR / "static"
STATIC_URL = "/static/"

# Analytics API_KEY (https://analytics.amplitude.com/famnom)
AMPLITUDE_API_KEY = config("AMPLITUDE_API_KEY")

# Caching spec
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": config("REDIS_URL"),
        "TIMEOUT": 300,  # seconds
        "KEY_PREFIX": "nourish",
        "OPTIONS": {
            "parser_class": "redis.connection.HiredisParser",
            "pool_class": "redis.BlockingConnectionPool",
        },
    }
}

SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=False, cast=bool)

# Rest framework settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework_api_key.permissions.HasAPIKey",
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "TEST_REQUEST_RENDERER_CLASSES": [
        "rest_framework.renderers.MultiPartRenderer",
        "rest_framework.renderers.JSONRenderer",
    ],
}

REST_AUTH_SERIALIZERS = {
    "USER_DETAILS_SERIALIZER": "nutrition_tracker.serializers.user.UserDataSerializer",
}

REST_AUTH_REGISTER_PERMISSION_CLASSES = {
    "rest_framework_api_key.permissions.HasAPIKey",
}

# Rest framework API Key
API_KEY_CUSTOM_HEADER = "HTTP_X_API_KEY"
