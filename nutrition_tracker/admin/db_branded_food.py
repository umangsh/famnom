"""Admin module for DB Branded Food."""
from __future__ import annotations

from django.contrib import admin

from nutrition_tracker.models import DBBrandedFood
from nutrition_tracker.utils import model as model_utils


@admin.register(DBBrandedFood)
class DBBrandedFoodAdmin(admin.ModelAdmin):
    """DB Branded Food Admin"""

    fields: list[str] = model_utils.get_field_names(
        list(DBBrandedFood._meta.fields), prefix_fields_in_order=["db_food"]
    )
    list_display: list[str] = model_utils.get_field_names(
        list(DBBrandedFood._meta.fields), prefix_fields_in_order=["db_food"]
    )
    raw_id_fields = ["db_food"]
    search_fields = ["db_food__id", "gtin_upc", "brand_owner"]
    ordering = ["db_food__id"]
