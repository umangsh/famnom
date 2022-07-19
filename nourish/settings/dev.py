"""Dev Django settings for nourish project."""
from __future__ import annotations

from decouple import config

from nourish.settings.base import *  # noqa F403 # pylint: disable=wildcard-import,unused-wildcard-import

DJANGO_ENV = "dev"
TEMPLATE_DEBUG = True
INTERNAL_IPS = ["127.0.0.1", "localhost", "0.0.0.0"]
SHELL_PLUS_PRINT_SQL_TRUNCATE = 100000

INSTALLED_APPS += [  # noqa F405
    "debug_toolbar",
]

MIDDLEWARE += [  # noqa F405
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "nourish",
        "USER": config("DB_USER", default=""),
        "PASSWORD": config("DB_PASSWORD", default=""),
        "HOST": "127.0.0.1",
        "PORT": "5432",
        "CONN_MAX_AGE": 10,
        "TEST": {
            "NAME": "test_nourish",
        },
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
    "loggers": {
        "django.template": {
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

DEBUG_TOOLBAR_PANELS = [
    "debug_toolbar.panels.history.HistoryPanel",
    "debug_toolbar.panels.versions.VersionsPanel",
    "debug_toolbar.panels.timer.TimerPanel",
    "debug_toolbar.panels.settings.SettingsPanel",
    "debug_toolbar.panels.headers.HeadersPanel",
    "debug_toolbar.panels.request.RequestPanel",
    "debug_toolbar.panels.sql.SQLPanel",
    "debug_toolbar.panels.staticfiles.StaticFilesPanel",
    "debug_toolbar.panels.templates.TemplatesPanel",
    "debug_toolbar.panels.cache.CachePanel",
    "debug_toolbar.panels.signals.SignalsPanel",
    "debug_toolbar.panels.logging.LoggingPanel",
    "debug_toolbar.panels.redirects.RedirectsPanel",
    "debug_toolbar.panels.profiling.ProfilingPanel",
]
