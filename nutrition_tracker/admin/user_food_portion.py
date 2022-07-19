"""Admin module for user food portion."""
from __future__ import annotations

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from nutrition_tracker.models import UserFoodPortion
from nutrition_tracker.utils import model as model_utils


@admin.register(UserFoodPortion)
class UserFoodPortionAdmin(admin.ModelAdmin):
    """User Food Portion Admin"""

    fields: list[str] = model_utils.get_field_names(
        list(UserFoodPortion._meta.fields), prefix_fields_in_order=["user"]
    )
    list_display: list[str] = model_utils.get_field_names(
        list(UserFoodPortion._meta.fields), prefix_fields_in_order=["user"]
    )
    search_fields = ["id", "object_id"]
    ordering = ["id"]


class UserFoodPortionAdminInline(GenericTabularInline):
    """User Food Portion Admin Inline"""

    model = UserFoodPortion
    extra = 0
