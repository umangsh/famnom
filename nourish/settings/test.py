"""Test Django settings for nourish project."""
from __future__ import annotations

import dj_database_url

from nourish.settings.base import *  # noqa F403 # pylint: disable=wildcard-import,unused-wildcard-import

DJANGO_ENV = "test"
TEMPLATE_DEBUG = False

db_config = dj_database_url.config()
DATABASES = {"default": db_config}
