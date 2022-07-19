"""Model and APIs for DB branded food metadata.

Data schema: {USDAFood, ...} => {DBFood} => {UserIngredient}
"""
from __future__ import annotations

from typing import Any, MutableMapping

from django.db import models
from django.db.models import QuerySet

from nutrition_tracker.database import models as db_models
from nutrition_tracker.models import db_food, id_base


class DBBrandedFood(id_base.IdBase):
    """DB Model for db branded food metadata."""

    db_food = models.OneToOneField(
        db_food.DBFood, on_delete=models.CASCADE, verbose_name="db_food", help_text="DB Food for this branded food."
    )
    brand_owner = models.TextField(
        null=True, blank=True, verbose_name="brand_owner", help_text="Brand owner for the food."
    )
    brand_name = models.TextField(
        null=True, blank=True, verbose_name="brand_name", help_text="Brand name for the food."
    )
    subbrand_name = models.TextField(
        null=True, blank=True, verbose_name="subbrand_name", help_text="Sub-brand name for the food."
    )
    gtin_upc = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="gtin_upc",
        help_text="GTIN or UPC code identifying the food.",
    )
    ingredients = models.TextField(
        null=True,
        blank=True,
        verbose_name="ingredients",
        help_text="The list of ingredients (as it appears on the product label).",
    )
    not_a_significant_source_of = models.TextField(null=True, blank=True, verbose_name="not_a_significant_source_of")

    class Meta(id_base.IdBase.Meta):
        db_table = "db_branded_food"
        indexes = [
            models.Index(name="db_branded_food_gtinupc_idx", fields=["gtin_upc"]),
        ]


def empty_qs() -> QuerySet[DBBrandedFood]:
    """Empty QuerySet."""
    return db_models.empty_qs(DBBrandedFood)


def _load_queryset() -> QuerySet[DBBrandedFood]:
    """Base QuerySet for db branded food. All other APIs filter on this queryset."""
    return DBBrandedFood.objects.select_related("db_food")


def load_cbranded_food(db_food_id: int | None = None) -> DBBrandedFood | None:
    """Loads a db branded food object."""
    params: dict[str, Any] = {}
    if db_food_id:
        params["db_food_id"] = db_food_id

    return db_models.load(DBBrandedFood, _load_queryset(), params)


def load_cbranded_foods(db_food_ids: list[int] | None = None, gtin_upc: str | None = None) -> QuerySet[DBBrandedFood]:
    """Batch load db branded food objects."""
    if not db_food_ids:
        db_food_ids = []

    qs: QuerySet[DBBrandedFood] = _load_queryset()

    params: dict[str, Any] = {}
    if db_food_ids:
        params["db_food_id__in"] = db_food_ids

    qs = db_models.bulk_load(qs, params)

    params = {}
    if gtin_upc:
        params["gtin_upc"] = gtin_upc

    return qs.filter(**params)


def create(**kwargs: Any) -> DBBrandedFood:
    """Create and save a db branded food row in the database."""
    return db_models.create(DBBrandedFood, **kwargs)


def update_or_create(defaults: MutableMapping[str, Any] | None = None, **kwargs: Any) -> tuple[DBBrandedFood, bool]:
    """Update a db branded food row with the given kwargs, creating a new one if necessary."""
    return db_models.update_or_create(DBBrandedFood, defaults=defaults, **kwargs)
