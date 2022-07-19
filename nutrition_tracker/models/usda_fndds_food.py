"""Model and APIs for USDA Survey FNDDS food metadata."""
from __future__ import annotations

from typing import Any, MutableMapping

from django.db import models
from django.db.models import QuerySet

from nutrition_tracker.database import models as db_models
from nutrition_tracker.models import db_base, usda_food


class USDAFnddsFood(db_base.DbBase):
    """DB Model for usda fndds food metadata."""

    usda_food = models.OneToOneField(
        usda_food.USDAFood,
        primary_key=True,
        on_delete=models.CASCADE,
        verbose_name="usda_food",
        help_text="USDA Food for this fndds food.",
    )
    food_code = models.PositiveBigIntegerField(
        null=True, blank=True, verbose_name="food_code", help_text="A unique ID identifying the food within FNDDS."
    )
    wweia_category_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="wweia_category_number",
        help_text=("Unique Identification number for WWEIA food category " "to which this food is assigned."),
    )
    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="start_date",
        help_text="Start date indicates time period corresponding to WWEIA data.",
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="end_date",
        help_text="End date indicates time period corresponding to WWEIA data.",
    )

    class Meta(db_base.DbBase.Meta):
        db_table = "usda_fndds_food"


def empty_qs() -> QuerySet[USDAFnddsFood]:
    """Empty QuerySet."""
    return db_models.empty_qs(USDAFnddsFood)


def _load_queryset() -> QuerySet[USDAFnddsFood]:
    """Base QuerySet for usda fndds food. All other APIs filter on this queryset."""
    return USDAFnddsFood.objects.select_related("usda_food")


def load_fndds_food(fdc_id: int | None = None) -> USDAFnddsFood | None:
    """Loads a usda fndds food object."""
    params: dict[str, Any] = {}
    if fdc_id:
        params["usda_food_id"] = fdc_id

    return db_models.load(USDAFnddsFood, _load_queryset(), params)


def load_fndds_foods(fdc_ids: list[int] | None = None) -> QuerySet[USDAFnddsFood]:
    """Batch load usda fndds food objects."""
    if not fdc_ids:
        fdc_ids = []

    qs: QuerySet[USDAFnddsFood] = _load_queryset()

    params: dict[str, Any] = {}
    if fdc_ids:
        params["usda_food_id__in"] = fdc_ids

    return db_models.bulk_load(qs, params)


def create(**kwargs: Any) -> USDAFnddsFood:
    """Create and save a usda fndds food row in the database."""
    return db_models.create(USDAFnddsFood, **kwargs)


def update_or_create(defaults: MutableMapping[str, Any] | None = None, **kwargs: Any) -> tuple[USDAFnddsFood, bool]:
    """Update a usda fndds food row with the given kwargs, creating a new one if necessary."""
    return db_models.update_or_create(USDAFnddsFood, defaults=defaults, **kwargs)
