"""Admin module for DB Food Nutrient."""
from __future__ import annotations

from django.contrib import admin

from nutrition_tracker.models import DBFoodNutrient
from nutrition_tracker.utils import model as model_utils


@admin.register(DBFoodNutrient)
class DBFoodNutrientAdmin(admin.ModelAdmin):
    """DB Food Nutrient Admin"""

    fields: list[str] = model_utils.get_field_names(
        list(DBFoodNutrient._meta.fields), prefix_fields_in_order=["db_food", "source_id", "source_type"]
    )
    list_display: list[str] = model_utils.get_field_names(
        list(DBFoodNutrient._meta.fields), prefix_fields_in_order=["db_food", "source_id", "source_type"]
    )
    raw_id_fields = ["db_food"]
    search_fields = ["db_food__id", "nutrient_id"]
    ordering = ["db_food__id"]
