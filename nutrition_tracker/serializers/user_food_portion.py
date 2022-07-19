"""UserFoodPortion serializer module."""
from __future__ import annotations

from fractions import Fraction

from rest_framework import serializers

from nutrition_tracker.constants import constants
from nutrition_tracker.models import UserFoodPortion
from nutrition_tracker.serializers import base


class UserFoodPortionSerializer(base.NonNullModelSerializer):
    """UserFoodPortion Serializer class."""

    household_quantity = serializers.SerializerMethodField()
    household_unit = serializers.SerializerMethodField()

    class Meta:
        model = UserFoodPortion
        fields = (
            "id",
            "external_id",
            "servings_per_container",
            "household_quantity",
            "household_unit",
            "serving_size",
            "serving_size_unit",
        )

    def get_household_quantity(self, obj: UserFoodPortion) -> str | None:  # pylint: disable=no-self-use
        """Get household quantity to be rendered in food forms."""
        return next(
            (unit_name for unit_name in constants.FORM_SERVING_SIZE_UNITS if obj.amount == float(Fraction(unit_name))),
            None,
        )

    def get_household_unit(self, obj: UserFoodPortion) -> str | None:  # pylint: disable=no-self-use
        """Get household unit to be rendered in food forms."""
        return str(obj.measure_unit_id) if obj.measure_unit_id is not None else None
