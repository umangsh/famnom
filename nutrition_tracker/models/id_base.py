"""DB Base Model with IDs. All DB Models with IDs as PK should be a child."""
from __future__ import annotations

from django.db import models

from nutrition_tracker.models import db_base


class IdBase(db_base.DbBase):
    """DB Base Model with IDs."""

    id = models.BigAutoField(primary_key=True)

    class Meta(db_base.DbBase.Meta):
        abstract = True
