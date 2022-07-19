"""Admin module for user preference threshold."""
from __future__ import annotations

from django.contrib import admin

from nutrition_tracker.models import UserPreferenceThreshold
from nutrition_tracker.utils import model as model_utils


@admin.register(UserPreferenceThreshold)
class UserPreferenceThresholdAdmin(admin.ModelAdmin):
    """User Preference Threshold Admin"""

    fields: list[str] = model_utils.get_field_names(
        list(UserPreferenceThreshold._meta.fields), prefix_fields_in_order=["user"]
    )
    list_display: list[str] = model_utils.get_field_names(
        list(UserPreferenceThreshold._meta.fields), prefix_fields_in_order=["user"]
    )
    search_fields = ["id"]
    ordering = ["id"]


class UserPreferenceThresholdAdminInline(admin.TabularInline):
    """User Preference Threshold Admin Inline"""

    model = UserPreferenceThreshold
    extra = 0
