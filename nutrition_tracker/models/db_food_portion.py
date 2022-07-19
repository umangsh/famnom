"""Model and APIs for DB food portion metadata.

Data schema: {USDAFood, ...} => {DBFood} => {UserIngredient}
"""
from __future__ import annotations

import uuid
from typing import Any, MutableMapping

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import QuerySet

from nutrition_tracker.constants import constants
from nutrition_tracker.database import models as db_models
from nutrition_tracker.models import db_food, id_base


class DBFoodPortion(id_base.IdBase):
    """DB Model for db food portion metadata."""

    db_food = models.ForeignKey(
        db_food.DBFood,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="db_food",
        help_text="DB Food for this food portion.",
    )
    source_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="source_id",
        help_text=(
            "Unique (per food) permanent identifier of the row "
            "in source dataset. For e.g. id for USDA Food Portions."
        ),
    )
    source_type = models.PositiveSmallIntegerField(
        default=constants.DBFoodSourceType.UNKNOWN,
        choices=constants.DBFoodSourceType.choices,
        verbose_name="source_type",
        help_text="Food source type.",
    )
    external_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    servings_per_container = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0)],
        verbose_name="servings_per_container",
        help_text="The number of servings per container.",
    )
    serving_size = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0)],
        verbose_name="serving_size",
        help_text="The amount of the serving size when expressed as gram or ml.",
    )
    serving_size_unit = models.CharField(
        max_length=25,
        null=True,
        blank=True,
        verbose_name="serving_size_unit",
        help_text="The unit used to express the serving size (gram or ml).",
    )
    quantity = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0)],
        verbose_name="quantity",
        help_text=("The quantity of portions used as specified by the user."),
    )
    amount = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0)],
        verbose_name="amount",
        help_text=(
            "The number of measure units that comprise the measure " "(e.g. if measure is 3 tsp, the amount is 3)."
        ),
    )
    measure_unit_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="measure_unit_id",
        help_text=("The unit used for the measure (e.g. if measure is 3 tsp, " "the unit is tsp)."),
    )
    portion_description = models.TextField(
        null=True,
        blank=True,
        verbose_name="portion_description",
        help_text=(
            "Foundation foods: Comments that provide more specificity "
            "on the measure. For example, for a pizza measure the "
            "dissemination text might be 1 slice is 1/8th of a 14 "
            "inch pizza. "
            "Survey (FNDDS) foods: The household description of the portion."
        ),
    )
    modifier = models.TextField(
        null=True,
        blank=True,
        verbose_name="modifier",
        help_text=(
            "Foundation foods: Qualifier of the measure (e.g. related "
            "to food shape or form) (e.g. melted, crushed, diced). "
            "Survey (FNDDS) foods: The portion code. "
            "SR legacy foods: description of measures, including the "
            'unit of measure and the measure modifier (e.g. waffle round (4" dia)).'
        ),
    )

    class Meta(id_base.IdBase.Meta):
        db_table = "db_food_portion"
        constraints = [
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_one_per_db_food_source_id_type",
                fields=["db_food", "source_id", "source_type"],
            ),
        ]


def empty_qs() -> QuerySet[DBFoodPortion]:
    """Empty QuerySet."""
    return db_models.empty_qs(DBFoodPortion)


def _load_queryset() -> QuerySet[DBFoodPortion]:
    """Base QuerySet for db food portions. All other APIs filter on this queryset."""
    return DBFoodPortion.objects.select_related("db_food")


def load_portion(id_: int | None = None, external_id: str | uuid.UUID | None = None) -> DBFoodPortion | None:
    """Loads a db food portion object."""
    params: dict[str, Any] = {}
    if id_:
        params["id"] = id_
    if external_id:
        params["external_id"] = external_id

    return db_models.load(DBFoodPortion, _load_queryset(), params)


def load_portions(
    ids: list[int] | None = None,
    external_ids: list[str | uuid.UUID] | None = None,
    db_food_ids: list[int] | None = None,
) -> QuerySet[DBFoodPortion]:
    """Batch load db food portion objects."""
    if not ids:
        ids = []
    if not external_ids:
        external_ids = []
    if not db_food_ids:
        db_food_ids = []

    qs: QuerySet[DBFoodPortion] = _load_queryset()

    params: dict[str, Any] = {}
    if ids:
        params["id__in"] = ids
    if external_ids:
        params["external_id__in"] = external_ids
    if db_food_ids:
        params["db_food_id__in"] = db_food_ids

    return db_models.bulk_load(qs, params)


def create(**kwargs: Any) -> DBFoodPortion:
    """Create and save a db food portion in the database."""
    return db_models.create(DBFoodPortion, **kwargs)


def update_or_create(defaults: MutableMapping[str, Any] | None = None, **kwargs: Any) -> tuple[DBFoodPortion, bool]:
    """Update a db food portion with the given kwargs, creating a new one if necessary."""
    return db_models.update_or_create(DBFoodPortion, defaults=defaults, **kwargs)
