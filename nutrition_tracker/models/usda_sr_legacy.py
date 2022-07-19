"""Model and APIs for USDA SR legacy food metadata."""
from __future__ import annotations

from typing import Any, MutableMapping

from django.db import models
from django.db.models import QuerySet

from nutrition_tracker.database import models as db_models
from nutrition_tracker.models import db_base, usda_food


class USDASRLegacy(db_base.DbBase):
    """DB Model for usda SR legacy food metadata."""

    usda_food = models.OneToOneField(
        usda_food.USDAFood,
        primary_key=True,
        on_delete=models.CASCADE,
        verbose_name="usda_food",
        help_text="USDA Food for this SR legacy food.",
    )
    ndb_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="ndb_number",
        help_text="Unique number assigned for the food, different from fdc_id, assigned in SR.",
    )

    class Meta(db_base.DbBase.Meta):
        db_table = "usda_sr_legacy"


def empty_qs() -> QuerySet[USDASRLegacy]:
    """Empty QuerySet."""
    return db_models.empty_qs(USDASRLegacy)


def _load_queryset() -> QuerySet[USDASRLegacy]:
    """Base QuerySet for usda SR legacy food. All other APIs filter on this queryset."""
    return USDASRLegacy.objects.select_related("usda_food")


def load_sr_legacy_food(fdc_id: int | None = None) -> USDASRLegacy | None:
    """Loads a usda SR legacy food object."""
    params: dict[str, Any] = {}
    if fdc_id:
        params["usda_food_id"] = fdc_id

    return db_models.load(USDASRLegacy, _load_queryset(), params)


def load_sr_legacy_foods(fdc_ids: list[int] | None = None, ndb_number: int | None = None) -> QuerySet[USDASRLegacy]:
    """Batch load usda SR legacy food objects."""
    if not fdc_ids:
        fdc_ids = []

    qs: QuerySet[USDASRLegacy] = _load_queryset()

    params: dict[str, Any] = {}
    if fdc_ids:
        params["usda_food_id__in"] = fdc_ids

    qs = db_models.bulk_load(qs, params)

    params = {}
    if ndb_number:
        params["ndb_number"] = ndb_number

    return qs.filter(**params)


def create(**kwargs: Any) -> USDASRLegacy:
    """Create and save a usda SR legacy food row in the database."""
    return db_models.create(USDASRLegacy, **kwargs)


def update_or_create(defaults: MutableMapping[str, Any] | None = None, **kwargs: Any) -> tuple[USDASRLegacy, bool]:
    """Update a usda SR legacy food row with the given kwargs, creating a new one if necessary."""
    return db_models.update_or_create(USDASRLegacy, defaults=defaults, **kwargs)
