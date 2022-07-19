"""Admin module for USDA Foundation Food."""
from __future__ import annotations

from django.contrib import admin

from nutrition_tracker.models import USDAFoundationFood
from nutrition_tracker.utils import model as model_utils


@admin.register(USDAFoundationFood)
class USDAFoundationFoodAdmin(admin.ModelAdmin):
    """USDA Foundation Food Admin"""

    fields: list[str] = model_utils.get_field_names(
        list(USDAFoundationFood._meta.fields), prefix_fields_in_order=["usda_food"]
    )
    list_display: list[str] = model_utils.get_field_names(
        list(USDAFoundationFood._meta.fields), prefix_fields_in_order=["usda_food"]
    )
    raw_id_fields = ["usda_food"]
    search_fields = ["usda_food__fdc_id"]
    ordering = ["usda_food__fdc_id"]
