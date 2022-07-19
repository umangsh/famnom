"""Admin module for user food/ingredient."""
from __future__ import annotations

from django.contrib import admin

from nutrition_tracker.admin import user_food_membership, user_food_portion
from nutrition_tracker.models import UserIngredient
from nutrition_tracker.utils import model as model_utils


@admin.register(UserIngredient)
class UserIngredientAdmin(admin.ModelAdmin):
    """User Food/Ingredient Admin"""

    fields: list[str] = model_utils.get_field_names(list(UserIngredient._meta.fields), prefix_fields_in_order=["name"])
    list_display: list[str] = model_utils.get_field_names(
        list(UserIngredient._meta.fields), prefix_fields_in_order=["name"]
    )
    readonly_fields = ["external_id"]
    search_fields = ["name", "external_id", "id"]
    autocomplete_fields = ["user"]
    ordering = ["name"]
    raw_id_fields = ["db_food"]
    inlines = [user_food_portion.UserFoodPortionAdminInline, user_food_membership.UserFoodMembershipChildAdminInline]
