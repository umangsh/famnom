"""Admin module for DB Food."""
from __future__ import annotations

from django.contrib import admin

from nutrition_tracker.models import DBFood
from nutrition_tracker.utils import model as model_utils


@admin.register(DBFood)
class DBFoodAdmin(admin.ModelAdmin):
    """DB Food Admin"""

    fields: list[str] = model_utils.get_field_names(
        list(DBFood._meta.fields), prefix_fields_in_order=["source_id", "source_type", "source_sub_type"]
    )
    list_display: list[str] = model_utils.get_field_names(
        list(DBFood._meta.fields), prefix_fields_in_order=["source_id", "source_type", "source_sub_type"]
    )
    readonly_fields = ["external_id"]
    search_fields = ["id", "source_id", "description", "external_id"]
    ordering = ["id"]
