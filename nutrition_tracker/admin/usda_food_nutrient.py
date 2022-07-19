"""Admin module for USDA Food Nutrient."""
from __future__ import annotations

from django.contrib import admin

from nutrition_tracker.models import USDAFoodNutrient
from nutrition_tracker.utils import model as model_utils


@admin.register(USDAFoodNutrient)
class USDAFoodNutrientAdmin(admin.ModelAdmin):
    """USDA Food Nutrient Admin"""

    fields: list[str] = model_utils.get_field_names(
        list(USDAFoodNutrient._meta.fields), prefix_fields_in_order=["id", "usda_food"]
    )
    list_display: list[str] = model_utils.get_field_names(
        list(USDAFoodNutrient._meta.fields), prefix_fields_in_order=["id", "usda_food"]
    )
    raw_id_fields = ["usda_food"]
    search_fields = ["id", "usda_food__fdc_id", "nutrient_id"]
    ordering = ["usda_food__fdc_id"]
