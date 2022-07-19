"""Admin module for USDA SR Legacy Food."""
from __future__ import annotations

from django.contrib import admin

from nutrition_tracker.models import USDASRLegacy
from nutrition_tracker.utils import model as model_utils


@admin.register(USDASRLegacy)
class USDASRLegacyAdmin(admin.ModelAdmin):
    """USDA Food Portion Admin"""

    fields: list[str] = model_utils.get_field_names(
        list(USDASRLegacy._meta.fields), prefix_fields_in_order=["usda_food"]
    )
    list_display: list[str] = model_utils.get_field_names(
        list(USDASRLegacy._meta.fields), prefix_fields_in_order=["usda_food"]
    )
    search_fields = ["usda_food__fdc_id"]
    ordering = ["usda_food__fdc_id"]
