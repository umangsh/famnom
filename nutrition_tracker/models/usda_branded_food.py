"""Model and APIs for USDA branded food metadata.

Data schema: {USDAFood, ...} => {DBFood} => {UserIngredient}
"""
from __future__ import annotations

from typing import Any, MutableMapping

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import QuerySet

from nutrition_tracker.database import models as db_models
from nutrition_tracker.models import db_base, usda_food


class USDABrandedFood(db_base.DbBase):
    """DB Model for usda branded food metadata."""

    usda_food = models.OneToOneField(
        usda_food.USDAFood,
        primary_key=True,
        on_delete=models.CASCADE,
        verbose_name="usda_food",
        help_text="USDA Food for this branded food.",
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
        help_text=(
            "GTIN or UPC code identifying the food."
            "Duplicate codes signify an update to the product,"
            "use the publication_date found in the food table"
            "to distinguish when each update was published, e.g."
            "the latest publication date will be the most recent"
            "update of the product."
        ),
    )
    ingredients = models.TextField(
        null=True,
        blank=True,
        verbose_name="ingredients",
        help_text="The list of ingredients (as it appears on the product label).",
    )
    not_a_significant_source_of = models.TextField(null=True, blank=True, verbose_name="not_a_significant_source_of")
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
    household_serving_fulltext = models.TextField(
        null=True,
        blank=True,
        verbose_name="household_serving_fulltext",
        help_text="Amount and unit of serving size when expressed in household units.",
    )
    branded_food_category = models.TextField(
        null=True,
        blank=True,
        verbose_name="branded_food_category",
        help_text="The category of the branded food, assigned by GDSN or Label Insight.",
    )
    data_source = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="data_source",
        help_text=("The source of the data for this food." "GDSN (for GS1) or LI (for Label Insight)."),
    )
    package_weight = models.TextField(
        null=True,
        blank=True,
        verbose_name="package_weight",
        help_text=("Package weight."),
    )
    modified_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="modified_date",
        help_text=(
            "This date reflects when the product data was last modified"
            "by the data provider, i.e., the manufacturer."
        ),
    )
    available_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="available_date",
        help_text=("This is the date when the product record was available" "for inclusion in the database."),
    )
    market_country = models.TextField(
        null=True,
        blank=True,
        verbose_name="market_country",
        help_text="The primary country where the product is marketed.",
    )
    discontinued_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="discontinued_date",
        help_text="This is the date when the product was discontinued.",
    )
    preparation_state_code = models.TextField(
        null=True,
        blank=True,
        verbose_name="preparation_state_code",
        help_text="Preparation state code.",
    )
    trade_channel = models.TextField(
        null=True,
        blank=True,
        verbose_name="trade_channel",
        help_text="Trade channel.",
    )

    class Meta(db_base.DbBase.Meta):
        db_table = "usda_branded_food"
        indexes = [
            models.Index(name="usda_branded_food_gtinupc_idx", fields=["gtin_upc"]),
        ]


def empty_qs() -> QuerySet[USDABrandedFood]:
    """Empty QuerySet."""
    return db_models.empty_qs(USDABrandedFood)


def _load_queryset() -> QuerySet[USDABrandedFood]:
    """Base QuerySet for usda branded food. All other APIs filter on this queryset."""
    return USDABrandedFood.objects.select_related("usda_food")


def load_cbranded_food(fdc_id: int | None = None) -> USDABrandedFood | None:
    """Loads a usda branded food object."""
    params: dict[str, Any] = {}
    if fdc_id:
        params["usda_food_id"] = fdc_id

    return db_models.load(USDABrandedFood, _load_queryset(), params)


def load_cbranded_foods(fdc_ids: list[int] | None = None, gtin_upc: str | None = None) -> QuerySet[USDABrandedFood]:
    """Batch load usda branded food objects."""
    if not fdc_ids:
        fdc_ids = []

    qs: QuerySet[USDABrandedFood] = _load_queryset()

    params: dict[str, Any] = {}
    if fdc_ids:
        params["usda_food_id__in"] = fdc_ids

    qs = db_models.bulk_load(qs, params)

    params = {}
    if gtin_upc:
        params["gtin_upc"] = gtin_upc

    return qs.filter(**params)


def create(**kwargs: Any) -> USDABrandedFood:
    """Create and save a usda branded food row in the database."""
    return db_models.create(USDABrandedFood, **kwargs)


def update_or_create(defaults: MutableMapping[str, Any] | None = None, **kwargs: Any) -> tuple[USDABrandedFood, bool]:
    """Update a usda branded food row with the given kwargs, creating a new one if necessary."""
    return db_models.update_or_create(USDABrandedFood, defaults=defaults, **kwargs)
