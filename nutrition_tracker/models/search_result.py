"""Model and APIs for search results."""
from __future__ import annotations

import uuid
from typing import Any

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.db import models
from django.db.models import QuerySet
from django.utils.functional import cached_property

from nutrition_tracker.constants import constants
from nutrition_tracker.database import models as db_models
from nutrition_tracker.models import id_base
from nutrition_tracker.utils import url_factory


class SearchResult(id_base.IdBase):
    """DB Model for search results."""

    external_id = models.UUIDField(
        unique=True, verbose_name="external_id", help_text="External ID of the indexed result."
    )
    search_vector = SearchVectorField(
        null=True, blank=True, editable=False, verbose_name="search_vector", help_text="Composite column to search on."
    )
    name = models.TextField(null=True, blank=True, verbose_name="name", help_text="Name of the search result.")
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
    category_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="food_category_id",
        help_text="Id of the food category the food belongs to.",
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

    class Meta(id_base.IdBase.Meta):
        db_table = "gt_search_index"
        indexes = [
            GinIndex(fields=["search_vector"]),
            models.Index(name="search_result_gtinupc_idx", fields=["gtin_upc"]),
        ]

    @cached_property
    def display_name(self) -> str | None:
        """Formatted search result name for display."""
        return self.name

    @cached_property
    def url(self) -> str:
        """Search Result URL."""
        return url_factory.get_food_url(self.external_id)

    @cached_property
    def display_brand_details(self) -> str:
        """Formatted brand details for display."""
        brand_fields = constants.BRAND_FIELDS[:-1]
        fieldvalues = [getattr(self, f, None) for f in brand_fields]
        return ", ".join([value for value in fieldvalues if value])


def empty_qs() -> QuerySet[SearchResult]:
    """Empty QuerySet."""
    return db_models.empty_qs(SearchResult)


def _load_queryset() -> QuerySet[SearchResult]:
    """Base QuerySet for search results. All other APIs filter on this queryset."""
    return SearchResult.objects.all()


def load_results(
    ids: list[int] | None = None,
    external_ids: list[str | uuid.UUID] | None = None,
    gtin_upc: str | None = None,
) -> QuerySet[SearchResult]:
    """Batch load search result objects."""
    if not ids:
        ids = []
    if not external_ids:
        external_ids = []

    qs: QuerySet[SearchResult] = _load_queryset()

    params: dict[str, Any] = {}
    if ids:
        params["id__in"] = ids
    if external_ids:
        params["external_id__in"] = external_ids
    if gtin_upc:
        params["gtin_upc"] = gtin_upc

    return db_models.bulk_load(qs, params)


def bulk_create(
    objs: list[SearchResult], batch_size: int | None = None, ignore_conflicts: bool = False
) -> list[SearchResult]:
    """Insert the provided list of search results into the database."""
    return db_models.bulk_create(SearchResult, objs, batch_size=batch_size, ignore_conflicts=ignore_conflicts)


def create(**kwargs: Any) -> SearchResult:
    """Create and save a search result in the database."""
    return db_models.create(SearchResult, **kwargs)


def update(**kwargs: Any) -> int:
    """Updates the search results model for the specified fields, and returns the number of rows matched."""
    return db_models.update(SearchResult, **kwargs)


def get_search_vector() -> SearchVector:
    """Search vector config used for search lookups."""
    return (
        SearchVector("name", config="english")
        + SearchVector("brand_name", config="english")
        + SearchVector("brand_owner", config="english")
        + SearchVector("subbrand_name", config="english")
        + SearchVector("gtin_upc", config="english")
    )


def update_search_vector() -> int:
    """Updates the search results model search vector field, and returns the number of rows matched."""
    return update(search_vector=get_search_vector())


def delete_all() -> None:
    """Delete all search result objects in the database."""
    _load_queryset().delete()
