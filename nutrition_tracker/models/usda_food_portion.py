"""Model and APIs for USDA food portion metadata.

Data schema: {USDAFood, ...} => {DBFood} => {UserIngredient}
"""
from __future__ import annotations

from typing import Any, MutableMapping

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import QuerySet

from nutrition_tracker.database import models as db_models
from nutrition_tracker.models import db_base, usda_food


class USDAFoodPortion(db_base.DbBase):
    """DB Model for usda food portion metadata."""

    id = models.PositiveBigIntegerField(
        primary_key=True, verbose_name="id", help_text="ID for the USDA Food Portion row."
    )
    usda_food = models.ForeignKey(
        usda_food.USDAFood,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="usda_food",
        help_text="USDA Food for this food portion.",
    )
    seq_num = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="seq_num",
        help_text="The order the measure will be displayed on the released food.",
    )
    amount = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0)],
        verbose_name="amount",
        help_text=(
            "The number of measure units that comprise the measure "
            "(e.g. if measure is 3 tsp, the amount is 3). Not defined "
            "for survey (FNDDS) foods (amount is instead embedded in "
            "portion description)."
        ),
    )
    measure_unit_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="measure_unit_id",
        help_text=(
            "The unit used for the measure (e.g. if measure is 3 tsp, "
            "the unit is tsp). For food types that do not use measure "
            "SR legacy foods and survey (FNDDS) foods), a value of "
            "'9999' is assigned to this field."
        ),
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
    gram_weight = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0)],
        verbose_name="gram_weight",
        help_text="The weight of the measure in grams.",
    )
    data_points = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="data_points",
        help_text="The number of observations on which the measure is based.",
    )
    footnote = models.TextField(
        null=True,
        blank=True,
        verbose_name="footnote",
        help_text=(
            "Comments on any unusual aspects of the measure. "
            "These are released to the public. Examples might "
            "include caveats on the usage of a measure, or reasons "
            "why a measure gram weight is an unexpected value."
        ),
    )
    min_year_acquired = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="min_year_acquired",
        help_text="Minimum purchase year of all acquisitions used to derive the measure value.",
    )

    class Meta(db_base.DbBase.Meta):
        db_table = "usda_food_portion"


def empty_qs() -> QuerySet[USDAFoodPortion]:
    """Empty QuerySet."""
    return db_models.empty_qs(USDAFoodPortion)


def _load_queryset() -> QuerySet[USDAFoodPortion]:
    """Base QuerySet for usda food portions. All other APIs filter on this queryset."""
    return USDAFoodPortion.objects.select_related("usda_food")


def load_portion(id_: int | None = None) -> USDAFoodPortion | None:
    """Loads a usda food portion object."""
    params: dict[str, Any] = {}
    if id_:
        params["id"] = id_

    return db_models.load(USDAFoodPortion, _load_queryset(), params)


def load_portions(ids: list[int] | None = None, fdc_ids: list[int] | None = None) -> QuerySet[USDAFoodPortion]:
    """Batch load usda food portion objects."""
    if not ids:
        ids = []
    if not fdc_ids:
        fdc_ids = []

    qs: QuerySet[USDAFoodPortion] = _load_queryset()

    params: dict[str, Any] = {}
    if ids:
        params["id__in"] = ids
    if fdc_ids:
        params["usda_food_id__in"] = fdc_ids

    return db_models.bulk_load(qs, params)


def create(**kwargs: Any) -> USDAFoodPortion:
    """Create and save a usda food portion in the database."""
    return db_models.create(USDAFoodPortion, **kwargs)


def update_or_create(defaults: MutableMapping[str, Any] | None = None, **kwargs: Any) -> tuple[USDAFoodPortion, bool]:
    """Update a usda food portion with the given kwargs, creating a new one if necessary."""
    return db_models.update_or_create(USDAFoodPortion, defaults=defaults, **kwargs)
