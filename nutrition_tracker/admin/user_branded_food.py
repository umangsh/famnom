"""Admin module for user branded food."""
from __future__ import annotations

from django.contrib import admin

from nutrition_tracker.models import UserBrandedFood
from nutrition_tracker.utils import model as model_utils


@admin.register(UserBrandedFood)
class UserBrandedFoodAdmin(admin.ModelAdmin):
    """User Branded Food Admin"""

    fields: list[str] = model_utils.get_field_names(
        list(UserBrandedFood._meta.fields), prefix_fields_in_order=["user"]
    )
    list_display: list[str] = model_utils.get_field_names(
        list(UserBrandedFood._meta.fields), prefix_fields_in_order=["user"]
    )
    search_fields = ["id", "ingredient__external_id"]
    ordering = ["id"]
