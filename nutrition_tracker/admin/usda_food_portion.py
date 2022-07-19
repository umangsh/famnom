"""Admin module for USDA Food Portion."""
from __future__ import annotations

from django.contrib import admin

from nutrition_tracker.models import USDAFoodPortion
from nutrition_tracker.utils import model as model_utils


@admin.register(USDAFoodPortion)
class USDAFoodPortionAdmin(admin.ModelAdmin):
    """USDA Food Portion Admin"""

    fields: list[str] = model_utils.get_field_names(
        list(USDAFoodPortion._meta.fields), prefix_fields_in_order=["id", "usda_food"]
    )
    list_display: list[str] = model_utils.get_field_names(
        list(USDAFoodPortion._meta.fields), prefix_fields_in_order=["id", "usda_food"]
    )
    raw_id_fields = ["usda_food"]
    search_fields = ["id", "usda_food__fdc_id", "measure_unit_id"]
    ordering = ["id"]
