"""DBBrandedFood serializer module."""
from __future__ import annotations

from nutrition_tracker.models import DBBrandedFood
from nutrition_tracker.serializers import base


class DBBrandedFoodSerializer(base.NonNullModelSerializer):
    """DBBrandedFood Serializer class."""

    class Meta:
        model = DBBrandedFood
        fields = (
            "brand_owner",
            "brand_name",
            "subbrand_name",
            "gtin_upc",
            "ingredients",
            "not_a_significant_source_of",
        )
