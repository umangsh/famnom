"""Model and APIs for DB food metadata.

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
from nutrition_tracker.models import id_base


class DBFood(id_base.IdBase):
    """DB Model for db food metadata."""

    external_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    source_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="source_id",
        help_text=("Unique permanent identifier of a food in source dataset." "For e.g. fdc_id for USDA Foods."),
    )
    source_type = models.PositiveSmallIntegerField(
        default=constants.DBFoodSourceType.UNKNOWN,
        choices=constants.DBFoodSourceType.choices,
        verbose_name="source_type",
        help_text="Food source type.",
    )
    source_sub_type = models.PositiveSmallIntegerField(
        default=constants.DBFoodSourceSubType.UNKNOWN,
        choices=constants.DBFoodSourceSubType.choices,
        verbose_name="source_sub_type",
        help_text="Food source sub type.",
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

    class Meta(id_base.IdBase.Meta):
        db_table = "db_food"
        constraints = [
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_one_per_source_id_type", fields=["source_id", "source_type"]
            ),
        ]

    @cached_property
    def display_name(self) -> str | None:
        """Formatted food name for display."""
        return self.description

    def display_brand_field(self, fieldname: str) -> str | None:
        """Formatted brand field for display."""
        if hasattr(self, "dbbrandedfood") and self.dbbrandedfood:
            fieldvalue = getattr(self.dbbrandedfood, fieldname, "")
            if fieldvalue:
                return fieldvalue

        return ""

    @cached_property
    def display_brand_details(self) -> str:
        """Formatted brand details for display."""
        brand_fields = constants.BRAND_FIELDS[:-1]
        fieldvalues = [self.display_brand_field(f) for f in brand_fields]
        return ", ".join([value for value in fieldvalues if value])


def empty_qs() -> QuerySet[DBFood]:
    """Empty QuerySet."""
    return db_models.empty_qs(DBFood)


def _load_queryset() -> QuerySet[DBFood]:
    """Base QuerySet for db foods. All other APIs filter on this queryset."""
    return DBFood.objects.select_related("dbbrandedfood").prefetch_related("dbfoodportion_set")


def load_cfood(
    id_: int | None = None,
    external_id: str | uuid.UUID | None = None,
    source_id: int | None = None,
    source_type: constants.DBFoodSourceType | None = None,
) -> DBFood | None:
    """Loads a db food object."""
    params: dict[str, Any] = {}
    if id_:
        params["id"] = id_
    if external_id:
        params["external_id"] = external_id
    if source_id:
        params["source_id"] = source_id
    if source_type:
        params["source_type"] = source_type

    return db_models.load(DBFood, _load_queryset(), params)


def load_cfoods(
    ids: list[int] | None = None,
    external_ids: list[str | uuid.UUID] | None = None,
    description: str | None = None,
    source_type: constants.DBFoodSourceType | None = None,
    source_sub_type: constants.DBFoodSourceSubType | None = None,
) -> QuerySet[DBFood]:
    """Batch load db food objects."""
    if not ids:
        ids = []
    if not external_ids:
        external_ids = []

    qs: QuerySet[DBFood] = _load_queryset()

    params: dict[str, Any] = {}
    if ids:
        params["id__in"] = ids
    if external_ids:
        params["external_id__in"] = external_ids

    qs = db_models.bulk_load(qs, params)

    params = {}
    if description:
        params["description"] = description
    if source_type:
        params["source_type"] = source_type
    if source_sub_type:
        params["source_sub_type"] = source_sub_type

    return qs.filter(**params)


def create(**kwargs: Any) -> DBFood:
    """Create and save a db food in the database."""
    return db_models.create(DBFood, **kwargs)


def get_or_create(**kwargs: Any) -> tuple[DBFood, bool]:
    """Lookup a db food, creating one if necessary in the database."""
    return db_models.update_or_create(DBFood, **kwargs)


def update_or_create(defaults: MutableMapping[str, Any] | None = None, **kwargs: Any) -> tuple[DBFood, bool]:
    """Update a db food with the given kwargs, creating a new one if necessary."""
    return db_models.update_or_create(DBFood, defaults=defaults, **kwargs)


def load_cfoods_iterator() -> Iterator[DBFood]:
    """Returns an iterator over all db foods."""
    return DBFood.objects.select_related("dbbrandedfood").all().iterator()
