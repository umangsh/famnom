"""Model and APIs for USDA food metadata.

Data schema: {USDAFood, ...} => {DBFood} => {UserIngredient}
"""
from __future__ import annotations

import uuid
from typing import Any, Iterator, MutableMapping

from django.db import models
from django.db.models import QuerySet
from django.utils.functional import cached_property

from nutrition_tracker.constants import constants
from nutrition_tracker.database import models as db_models
from nutrition_tracker.models import db_base


class USDAFood(db_base.DbBase):
    """DB Model for usda food metadata."""

    external_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    fdc_id = models.PositiveBigIntegerField(
        primary_key=True, verbose_name="fdc_id", help_text="Unique permanent USDA identifier of a food."
    )
    data_type = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="data_type", help_text="Type of food data."
    )
    description = models.TextField(
        null=True, blank=True, verbose_name="description", help_text="Description of the food."
    )
    food_category_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="food_category_id",
        help_text="Id of the food category the food belongs to.",
    )
    publication_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="publication_date",
        help_text="Date when the food was published to FoodData Central.",
    )

    class Meta(db_base.DbBase.Meta):
        db_table = "usda_food"
        indexes = [
            models.Index(name="usda_food_description_type_idx", fields=["description", "data_type"]),
        ]

    @cached_property
    def display_name(self) -> str | None:
        """Formatted food name for display."""
        return self.description

    def display_brand_field(self, fieldname: str) -> str | None:
        """Formatted brand field for display."""
        if hasattr(self, "usdabrandedfood") and self.usdabrandedfood:
            fieldvalue = getattr(self.usdabrandedfood, fieldname, "")
            if fieldvalue:
                return fieldvalue

        return ""

    @cached_property
    def display_brand_details(self) -> str:
        """Formatted brand details for display."""
        brand_fields = constants.BRAND_FIELDS[:-1]
        fieldvalues = [self.display_brand_field(f) for f in brand_fields]
        return ", ".join([value for value in fieldvalues if value])


def empty_qs() -> QuerySet[USDAFood]:
    """Empty QuerySet."""
    return db_models.empty_qs(USDAFood)


def _load_queryset() -> QuerySet[USDAFood]:
    """Base QuerySet for usda foods. All other APIs filter on this queryset."""
    return USDAFood.objects.select_related("usdabrandedfood").prefetch_related("usdafoodportion_set")


def load_cfood(fdc_id: int | None = None, external_id: str | uuid.UUID | None = None) -> USDAFood | None:
    """Loads a usda food object."""
    params: dict[str, Any] = {}
    if fdc_id:
        params["fdc_id"] = fdc_id
    if external_id:
        params["external_id"] = external_id

    return db_models.load(USDAFood, _load_queryset(), params)


def load_cfoods(
    fdc_ids: list[int] | None = None,
    external_ids: list[str | uuid.UUID] | None = None,
    description: str | None = None,
    data_types: list[str] | None = None,
) -> QuerySet[USDAFood]:
    """Batch load usda food objects."""
    if not fdc_ids:
        fdc_ids = []
    if not external_ids:
        external_ids = []
    if not data_types:
        data_types = []

    qs: QuerySet[USDAFood] = _load_queryset()

    params: dict[str, Any] = {}
    if fdc_ids:
        params["fdc_id__in"] = fdc_ids
    if external_ids:
        params["external_id__in"] = external_ids

    qs = db_models.bulk_load(qs, params)

    params = {}
    if description:
        params["description"] = description
    if data_types:
        params["data_type__in"] = data_types

    qs = qs.filter(**params)
    return qs


def create(**kwargs: Any) -> USDAFood:
    """Create and save a usda food in the database."""
    return db_models.create(USDAFood, **kwargs)


def get_or_create(**kwargs: Any) -> tuple[USDAFood, bool]:
    """Lookup a usda food, creating one if necessary in the database."""
    return db_models.update_or_create(USDAFood, **kwargs)


def update_or_create(defaults: MutableMapping[str, Any] | None = None, **kwargs: Any) -> tuple[USDAFood, bool]:
    """Update a usda food with the given kwargs, creating a new one if necessary."""
    return db_models.update_or_create(USDAFood, defaults=defaults, **kwargs)


def load_cfoods_iterator(
    start: int | None = None, rows: int | None = None, data_types: list[str] | None = None
) -> Iterator[USDAFood] | QuerySet[USDAFood]:
    """Returns an iterator over all usda foods."""
    if start is None:
        start = 0
    if rows is None:
        rows = 0
    if data_types is None:
        data_types = constants.USDA_DATA_TYPES

    qs: QuerySet[USDAFood] = (
        USDAFood.objects.select_related("usdabrandedfood", "usdafoundationfood", "usdasrlegacy")
        .prefetch_related("usdafoodportion_set", "usdafoodnutrient_set")
        .filter(data_type__in=data_types)
    )

    # Slicing and iteration don't work together.
    # Return the sliced queryset if start/rows are specified.
    if start > 0:
        if not rows:
            return qs[start:]

        return qs[start : start + rows]

    if rows > 0:
        return qs[0:rows]

    return qs.iterator()
