"""FDA nutrition RDIs serializer module."""
from __future__ import annotations

from nutrition_tracker.models import UserPreference, UserPreferenceThreshold
from nutrition_tracker.serializers import base


class UserPreferenceThresholdSerializer(base.NonNullModelSerializer):
    """User preference threshold serializer class."""

    class Meta:
        model = UserPreferenceThreshold
        fields = (
            "min_value",
            "max_value",
            "exact_value",
        )


class UserPreferenceSerializer(base.DynamicFieldsModelSerializer, base.NonNullModelSerializer):
    """User preference serializer class."""

    thresholds = UserPreferenceThresholdSerializer(source="userpreferencethreshold_set", many=True)

    non_null_fields = [
        "food_external_id",
        "food_nutrient_id",
    ]

    class Meta:
        model = UserPreference
        fields = (
            "food_external_id",
            "food_nutrient_id",
            "thresholds",
        )
