"""Admin module for Search Result."""
from __future__ import annotations

from django.contrib import admin

from nutrition_tracker.models import SearchResult
from nutrition_tracker.utils import model as model_utils


@admin.register(SearchResult)
class SearchResultAdmin(admin.ModelAdmin):
    """Search Result Admin"""

    fields: list[str] = model_utils.get_field_names(list(SearchResult._meta.fields), prefix_fields_in_order=["name"])
    list_display: list[str] = model_utils.get_field_names(
        list(SearchResult._meta.fields), prefix_fields_in_order=["name"]
    )
    readonly_fields = ["external_id"]
    search_fields = ["name", "external_id", "brand_name", "brand_owner", "subbrand_name", "gtin_upc"]
