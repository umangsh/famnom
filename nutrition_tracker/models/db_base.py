"""DB Base Model. All DB Models should be a child."""
from __future__ import annotations

from django.db import models


class DbBase(models.Model):
    """DB Base Model."""

    created_timestamp = models.DateTimeField(auto_now_add=True)
    updated_timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
