"""Admin module for USDA Branded Food."""
from __future__ import annotations

from django.contrib import admin

from nutrition_tracker.models import USDABrandedFood
from nutrition_tracker.utils import model as model_utils


@admin.register(USDABrandedFood)
class USDABrandedFoodAdmin(admin.ModelAdmin):
    """USDA Branded Food Admin"""

    fields: list[str] = model_utils.get_field_names(
        list(USDABrandedFood._meta.fields), prefix_fields_in_order=["usda_food"]
    )
    list_display: list[str] = model_utils.get_field_names(
        list(USDABrandedFood._meta.fields), prefix_fields_in_order=["usda_food"]
    )
    raw_id_fields = ["usda_food"]
    search_fields = ["usda_food__fdc_id", "gtin_upc", "brand_owner"]
    ordering = ["usda_food__fdc_id"]
