"""Admin module for user meal."""
from __future__ import annotations

from django.contrib import admin

from nutrition_tracker.admin import user_food_membership, user_food_portion
from nutrition_tracker.models import UserMeal
from nutrition_tracker.utils import model as model_utils


@admin.register(UserMeal)
class UserMealAdmin(admin.ModelAdmin):
    """User Meal Admin"""

    fields: list[str] = model_utils.get_field_names(
        list(UserMeal._meta.fields), prefix_fields_in_order=["meal_type", "meal_date"]
    )
    list_display: list[str] = model_utils.get_field_names(
        list(UserMeal._meta.fields), prefix_fields_in_order=["meal_type", "meal_date"]
    )
    readonly_fields = ["external_id"]
    autocomplete_fields = ["user"]
    search_fields = ["meal_type"]
    inlines = [user_food_portion.UserFoodPortionAdminInline, user_food_membership.UserFoodMembershipParentAdminInline]
