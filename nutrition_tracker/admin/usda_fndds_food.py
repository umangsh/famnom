"""Admin module for USDA Survey FNDDS Food."""
from __future__ import annotations

from django.contrib import admin

from nutrition_tracker.models import USDAFnddsFood
from nutrition_tracker.utils import model as model_utils


@admin.register(USDAFnddsFood)
class USDAFnddsFoodAdmin(admin.ModelAdmin):
    """USDA Survey FNDDS Food Admin"""

    fields: list[str] = model_utils.get_field_names(
        list(USDAFnddsFood._meta.fields), prefix_fields_in_order=["usda_food"]
    )
    list_display: list[str] = model_utils.get_field_names(
        list(USDAFnddsFood._meta.fields), prefix_fields_in_order=["usda_food"]
    )
    raw_id_fields = ["usda_food"]
    search_fields = ["usda_food__fdc_id"]
    ordering = ["usda_food__fdc_id"]
