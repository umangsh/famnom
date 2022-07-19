"""DB Base Model for user generated data. All DB Models storing user generated data should be a child."""
from __future__ import annotations

from django.conf import settings
from django.db import models

from nutrition_tracker.models import id_base


class UserBase(id_base.IdBase):
    """DB Base Model for user generated data."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="owner user",
        help_text="User that owns the row.",
    )

    class Meta(id_base.IdBase.Meta):
        abstract = True
