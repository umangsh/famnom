"""Prod Django settings for nourish project."""
from __future__ import annotations

import os

import dj_database_url
import django_heroku
import sentry_sdk
from decouple import config
from sentry_sdk.integrations.django import DjangoIntegration

from nourish.settings.base import *  # noqa F403 # pylint: disable=wildcard-import,unused-wildcard-import

# Setup Sentry
sentry_sdk.init(
    dsn=config("SENTRY_DSN"),
    integrations=[DjangoIntegration()],
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production,
    traces_sample_rate=config("SENTRY_TRACES_SAMPLE_RATE", default=1.0, cast=float),
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=config("SENTRY_SEND_DEFAULT_PII", default=False, cast=bool),
    # By default the SDK will try to use the SENTRY_RELEASE
    # environment variable, or infer a git commit
    # SHA as release, however you may want to set
    # something more human-readable.
    # release="myapp@1.0.0",
    environment=config("SENTRY_ENVIRONMENT"),
)

DJANGO_ENV = "prod"
TEMPLATE_DEBUG = False

db_config = dj_database_url.config(
    env="DATABASE_CONNECTION_POOL_URL",
    default=os.environ.get("DATABASE_URL"),
    conn_max_age=600,
    ssl_require=True,
)
DATABASES = {"default": db_config}

SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 60
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Activate Django-Heroku.
# It provides many niceties, including the reading of DATABASE_URL,
# logging configuration, a Heroku CI–compatible TestRunner,
# and automatically configures ‘staticfiles’ to “just work”.
django_heroku.settings(locals())
