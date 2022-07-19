"""Admin module for user food nutrient."""
from __future__ import annotations

from django.contrib import admin

from nutrition_tracker.models import UserFoodNutrient
from nutrition_tracker.utils import model as model_utils


@admin.register(UserFoodNutrient)
class UserFoodNutrientAdmin(admin.ModelAdmin):
    """User Food Nutrient Admin"""

    fields: list[str] = model_utils.get_field_names(
        list(UserFoodNutrient._meta.fields), prefix_fields_in_order=["user"]
    )
    list_display: list[str] = model_utils.get_field_names(
        list(UserFoodNutrient._meta.fields), prefix_fields_in_order=["user"]
    )
    search_fields = ["id", "ingredient__external_id"]
    ordering = ["id"]
