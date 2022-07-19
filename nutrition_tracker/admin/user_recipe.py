"""Admin module for user recipe."""
from __future__ import annotations

from django.contrib import admin

from nutrition_tracker.admin import user_food_portion
from nutrition_tracker.models import UserRecipe
from nutrition_tracker.utils import model as model_utils


@admin.register(UserRecipe)
class UserRecipeAdmin(admin.ModelAdmin):
    """User Recipe Admin."""

    fields: list[str] = model_utils.get_field_names(
        list(UserRecipe._meta.fields), prefix_fields_in_order=["name", "recipe_date"]
    )
    list_display: list[str] = model_utils.get_field_names(
        list(UserRecipe._meta.fields), prefix_fields_in_order=["name", "recipe_date"]
    )
    readonly_fields = ["external_id"]
    autocomplete_fields = ["user"]
    search_fields = ["name", "external_id"]
    ordering = ("-recipe_date",)
    inlines = [user_food_portion.UserFoodPortionAdminInline]
