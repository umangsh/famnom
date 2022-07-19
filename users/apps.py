"""Application config metadata for users."""
from __future__ import annotations

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Configure application attributes for users."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
