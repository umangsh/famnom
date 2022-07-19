"""Admin module for DB Food Portion."""
from __future__ import annotations

from django.contrib import admin

from nutrition_tracker.models import DBFoodPortion
from nutrition_tracker.utils import model as model_utils


@admin.register(DBFoodPortion)
class DBFoodPortionAdmin(admin.ModelAdmin):
    """DB Food Portion Admin"""

    fields: list[str] = model_utils.get_field_names(
        list(DBFoodPortion._meta.fields), prefix_fields_in_order=["db_food", "source_id", "source_type"]
    )
    list_display: list[str] = model_utils.get_field_names(
        list(DBFoodPortion._meta.fields), prefix_fields_in_order=["db_food", "source_id", "source_type"]
    )
    raw_id_fields = ["db_food"]
    readonly_fields = ["external_id"]
    search_fields = ["db_food__id", "measure_unit_id"]
    ordering = ["id"]
