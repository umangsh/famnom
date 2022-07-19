"""Admin module for user preferences."""
from __future__ import annotations

from bitfield import BitField
from bitfield.forms import BitFieldCheckboxSelectMultiple
from django.contrib import admin

from nutrition_tracker.admin import user_preference_threshold
from nutrition_tracker.models import UserPreference
from nutrition_tracker.utils import model as model_utils


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    """User Preference Admin"""

    formfield_overrides = {
        BitField: {"widget": BitFieldCheckboxSelectMultiple},
    }
    fields: list[str] = model_utils.get_field_names(list(UserPreference._meta.fields), prefix_fields_in_order=["user"])
    list_display: list[str] = model_utils.get_field_names(
        list(UserPreference._meta.fields), prefix_fields_in_order=["user"]
    )
    search_fields = ["food_external_id", "food_category_id", "food_nutrient_id"]
    ordering = ["id"]
    inlines = [user_preference_threshold.UserPreferenceThresholdAdminInline]
