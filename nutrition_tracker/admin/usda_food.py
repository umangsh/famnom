"""Admin module for USDA Food."""
from __future__ import annotations

from django.contrib import admin

from nutrition_tracker.models import USDAFood
from nutrition_tracker.utils import model as model_utils


@admin.register(USDAFood)
class USDAFoodAdmin(admin.ModelAdmin):
    """USDA Food Admin"""

    fields: list[str] = model_utils.get_field_names(list(USDAFood._meta.fields), prefix_fields_in_order=["fdc_id"])
    list_display: list[str] = model_utils.get_field_names(
        list(USDAFood._meta.fields), prefix_fields_in_order=["fdc_id"]
    )
    readonly_fields = ["external_id"]
    search_fields = ["fdc_id", "description", "external_id", "data_type"]
    ordering = ["fdc_id"]
