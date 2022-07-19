"""Model and APIs for USDA foundation food metadata."""
from __future__ import annotations

from typing import Any, MutableMapping

from django.db import models
from django.db.models import QuerySet

from nutrition_tracker.database import models as db_models
from nutrition_tracker.models import db_base, usda_food


class USDAFoundationFood(db_base.DbBase):
    """DB Model for usda foundation food metadata."""

    usda_food = models.OneToOneField(
        usda_food.USDAFood,
        primary_key=True,
        on_delete=models.CASCADE,
        verbose_name="usda_food",
        help_text="USDA Food for this foundation food.",
    )
    ndb_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="ndb_number",
        help_text="Unique number assigned for the food, different from fdc_id, assigned in SR.",
    )
    footnote = models.TextField(
        null=True,
        blank=True,
        verbose_name="footnote",
        help_text=(
            "Comments on any unusual aspects. These are released to the public."
            "Examples might include unusual aspects of the food overall."
        ),
    )

    class Meta(db_base.DbBase.Meta):
        db_table = "usda_foundation_food"


def empty_qs() -> QuerySet[USDAFoundationFood]:
    """Empty QuerySet."""
    return db_models.empty_qs(USDAFoundationFood)


def _load_queryset() -> QuerySet[USDAFoundationFood]:
    """Base QuerySet for usda foundation food. All other APIs filter on this queryset."""
    return USDAFoundationFood.objects.select_related("usda_food")


def load_foundation_food(fdc_id: int | None = None) -> USDAFoundationFood | None:
    """Loads a usda foundation food object."""
    params: dict[str, Any] = {}
    if fdc_id:
        params["usda_food_id"] = fdc_id

    return db_models.load(USDAFoundationFood, _load_queryset(), params)


def load_foundation_foods(
    fdc_ids: list[int] | None = None, ndb_number: str | None = None
) -> QuerySet[USDAFoundationFood]:
    """Batch load usda foundation food objects."""
    if not fdc_ids:
        fdc_ids = []

    qs: QuerySet[USDAFoundationFood] = _load_queryset()

    params: dict[str, Any] = {}
    if fdc_ids:
        params["usda_food_id__in"] = fdc_ids

    qs = db_models.bulk_load(qs, params)

    params = {}
    if ndb_number:
        params["ndb_number"] = ndb_number

    return qs.filter(**params)


def create(**kwargs: Any) -> USDAFoundationFood:
    """Create and save a usda foundation food row in the database."""
    return db_models.create(USDAFoundationFood, **kwargs)


def update_or_create(
    defaults: MutableMapping[str, Any] | None = None, **kwargs: Any
) -> tuple[USDAFoundationFood, bool]:
    """Update a usda foundation food row with the given kwargs, creating a new one if necessary."""
    return db_models.update_or_create(USDAFoundationFood, defaults=defaults, **kwargs)
