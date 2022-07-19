"""Model and APIs for DB food nutrient.

Data schema: {USDAFood, ...} => {DBFood} => {UserIngredient}
"""
from __future__ import annotations

from typing import Any, MutableMapping

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import QuerySet

from nutrition_tracker.constants import constants
from nutrition_tracker.database import models as db_models
from nutrition_tracker.models import db_food, id_base


class DBFoodNutrient(id_base.IdBase):
    """DB Model for db food nutrient metadata."""

    db_food = models.ForeignKey(
        db_food.DBFood,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="db_food",
        help_text="DB Food for this food nutrient.",
    )
    source_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="source_id",
        help_text=("Unique permanent identifier of the row in source dataset." "For e.g. id for USDA Food Nutrients."),
    )
    source_type = models.PositiveSmallIntegerField(
        default=constants.DBFoodSourceType.UNKNOWN,
        choices=constants.DBFoodSourceType.choices,
        verbose_name="source_type",
        help_text="Food source type.",
    )
    nutrient_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="nutrient_id",
        help_text="ID of the nutrient to which the food nutrient pertains.",
    )
    amount = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0)],
        verbose_name="amount",
        help_text=("Amount of the nutrient per 100g of food. " "Specified in unit defined in the nutrient table."),
    )

    class Meta(id_base.IdBase.Meta):
        db_table = "db_food_nutrient"
        constraints = [
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_one_per_source_id_type", fields=["source_id", "source_type"]
            ),
        ]


def empty_qs() -> QuerySet[DBFoodNutrient]:
    """Empty QuerySet."""
    return db_models.empty_qs(DBFoodNutrient)


def _load_queryset() -> QuerySet[DBFoodNutrient]:
    """Base QuerySet for db food nutrients. All other APIs filter on this queryset."""
    return DBFoodNutrient.objects.select_related("db_food")


def load_nutrient(id_: int | None = None) -> DBFoodNutrient | None:
    """Loads a db food nutrient object."""
    params: dict[str, Any] = {}
    if id_:
        params["id"] = id_

    return db_models.load(DBFoodNutrient, _load_queryset(), params)


# flake8: noqa: C901
def load_nutrients(  # pylint: disable=too-many-arguments,too-many-branches
    ids: list[int] | None = None,
    db_food_ids: list[int] | None = None,
    db_source_types: list[constants.DBFoodSourceType] | None = None,
    db_source_sub_types: list[constants.DBFoodSourceSubType] | None = None,
    nutrient_ids: list[int] | None = None,
    order_by: str | None = None,
    max_rows: int | None = None,
    exclude_food_names: list[str] | None = None,
) -> QuerySet[DBFoodNutrient]:
    """Batch load db food nutrient objects."""
    if not ids:
        ids = []
    if not db_food_ids:
        db_food_ids = []
    if not db_source_types:
        db_source_types = []
    if not db_source_sub_types:
        db_source_sub_types = []
    if not nutrient_ids:
        nutrient_ids = []
    if not exclude_food_names:
        exclude_food_names = []

    qs: QuerySet[DBFoodNutrient] = _load_queryset()
    if order_by:
        qs = qs.order_by(order_by)

    params: dict[str, Any] = {}
    if ids:
        params["id__in"] = ids
    if db_food_ids:
        params["db_food_id__in"] = db_food_ids

    qs = db_models.bulk_load(qs, params)

    params = {}
    if db_source_types:
        params["db_food__source_type__in"] = db_source_types
    if db_source_sub_types:
        params["db_food__source_sub_type__in"] = db_source_sub_types
    if nutrient_ids:
        params["nutrient_id__in"] = nutrient_ids

    qs = qs.filter(**params)

    params = {}
    if exclude_food_names:
        for name in exclude_food_names:
            params["db_food__description__icontains"] = name
            qs = qs.exclude(**params)

    if max_rows:
        qs = qs[:max_rows]

    return qs


def create(**kwargs: Any) -> DBFoodNutrient:
    """Create and save a db food nutrient in the database."""
    return db_models.create(DBFoodNutrient, **kwargs)


def update_or_create(defaults: MutableMapping[str, Any] | None = None, **kwargs: Any) -> tuple[DBFoodNutrient, bool]:
    """Update a db food nutrient with the given kwargs, creating a new one if necessary."""
    return db_models.update_or_create(DBFoodNutrient, defaults=defaults, **kwargs)
