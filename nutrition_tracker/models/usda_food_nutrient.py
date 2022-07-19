"""Model and APIs for USDA food nutrient metadata.

Data schema: {USDAFood, ...} => {DBFood} => {UserIngredient}
"""
from __future__ import annotations

from typing import Any, MutableMapping

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import QuerySet

from nutrition_tracker.database import models as db_models
from nutrition_tracker.models import db_base, usda_food


class USDAFoodNutrient(db_base.DbBase):
    """DB Model for usda food nutrient metadata."""

    id = models.PositiveBigIntegerField(
        primary_key=True, verbose_name="id", help_text="ID for the USDA Food Nutrient row."
    )
    usda_food = models.ForeignKey(
        usda_food.USDAFood,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="usda_food",
        help_text="USDA Food for this food nutrient.",
    )
    nutrient_id = models.PositiveIntegerField(
        verbose_name="nutrient_id", help_text="ID of the nutrient to which the food nutrient pertains."
    )
    amount = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0)],
        verbose_name="amount",
        help_text=("Amount of the nutrient per 100g of food. " "Specified in unit defined in the nutrient table."),
    )
    data_points = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="data_points",
        help_text="Number of observations on which the value is based.",
    )
    derivation_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="derivation_id",
        help_text="ID of the food nutrient derivation technique used to derive the value.",
    )
    min = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0.0)], verbose_name="min", help_text="The minimum amount."
    )
    max = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0.0)], verbose_name="max", help_text="The maximum amount."
    )
    median = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0)],
        verbose_name="median",
        help_text="The median amount.",
    )
    loq = models.TextField(
        null=True,
        blank=True,
        verbose_name="loq",
        help_text="loq",
    )
    footnote = models.TextField(
        null=True,
        blank=True,
        verbose_name="footnote",
        help_text=(
            "Comments on any unusual aspects of the food nutrient. "
            "Examples might include why a nutrient value is different "
            "than typically expected."
        ),
    )
    min_year_acquired = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="min_year_acquired",
        help_text="Minimum purchase year of all acquisitions used to derive the nutrient value.",
    )

    class Meta(db_base.DbBase.Meta):
        db_table = "usda_food_nutrient"


def empty_qs() -> QuerySet[USDAFoodNutrient]:
    """Empty QuerySet."""
    return db_models.empty_qs(USDAFoodNutrient)


def _load_queryset() -> QuerySet[USDAFoodNutrient]:
    """Base QuerySet for usda food nutrients. All other APIs filter on this queryset."""
    return USDAFoodNutrient.objects.select_related("usda_food")


def load_nutrient(id_: int | None = None) -> USDAFoodNutrient | None:
    """Loads a usda food nutrient object."""
    params: dict[str, Any] = {}
    if id_:
        params["id"] = id_

    return db_models.load(USDAFoodNutrient, _load_queryset(), params)


# flake8: noqa: C901
def load_nutrients(  # pylint: disable=too-many-arguments,too-many-branches
    ids: list[int] | None = None,
    fdc_ids: list[int] | None = None,
    food_types: list[str] | None = None,
    nutrient_ids: list[int] | None = None,
    order_by: str | None = None,
    max_rows: int | None = None,
    exclude_food_names: list[str] | None = None,
) -> QuerySet[USDAFoodNutrient]:
    """Batch load usda food nutrient objects."""
    if not ids:
        ids = []
    if not fdc_ids:
        fdc_ids = []
    if not food_types:
        food_types = []
    if not nutrient_ids:
        nutrient_ids = []
    if not exclude_food_names:
        exclude_food_names = []

    qs: QuerySet[USDAFoodNutrient] = _load_queryset()
    if order_by:
        qs = qs.order_by(order_by)

    params: dict[str, Any] = {}
    if ids:
        params["id__in"] = ids
    if fdc_ids:
        params["usda_food_id__in"] = fdc_ids

    qs = db_models.bulk_load(qs, params)

    params = {}
    if food_types:
        params["usda_food__data_type__in"] = food_types
    if nutrient_ids:
        params["nutrient_id__in"] = nutrient_ids

    qs = qs.filter(**params)

    params = {}
    if exclude_food_names:
        for name in exclude_food_names:
            params["usda_food__description__icontains"] = name
            qs = qs.exclude(**params)

    if max_rows:
        qs = qs[:max_rows]

    return qs


def create(**kwargs: Any) -> USDAFoodNutrient:
    """Create and save a usda food nutrient in the database."""
    return db_models.create(USDAFoodNutrient, **kwargs)


def update_or_create(defaults: MutableMapping[str, Any] | None = None, **kwargs: Any) -> tuple[USDAFoodNutrient, bool]:
    """Update a usda food nutrient with the given kwargs, creating a new one if necessary."""
    return db_models.update_or_create(USDAFoodNutrient, defaults=defaults, **kwargs)
