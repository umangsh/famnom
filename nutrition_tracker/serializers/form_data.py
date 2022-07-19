"""FormData serializer module."""
from __future__ import annotations

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import food_category, food_portion


class FormDataSerializer:
    """Form data constants serializer class."""

    @classmethod
    def get_category_data(cls) -> list[dict]:
        """Return category data constants."""
        values = []
        for (key, value) in food_category.for_display_choices():
            values.append(
                {
                    "id": key,
                    "name": value,
                }
            )

        return values

    @classmethod
    def get_household_quantity_data(cls) -> list:
        """Return household quantity names."""
        values = [{"id": "", "name": "Select quantity"}]
        for unit in constants.FORM_SERVING_SIZE_UNITS:
            values.append(
                {
                    "id": unit,
                    "name": unit,
                }
            )

        return values

    @classmethod
    def get_household_unit_data(cls) -> list[dict]:
        """Return household unit names."""
        values = [{"id": "", "name": "Select unit"}]
        for fportion in food_portion.get_measure_units_sorted_by_name():
            values.append(
                {
                    "id": str(fportion.id_),
                    "name": fportion.name,
                }
            )

        return values

    @classmethod
    def get_serving_size_unit_data(cls) -> list:
        """Return household quantity names."""
        values = []
        for (key, value) in constants.ServingSizeUnit.choices:
            values.append(
                {
                    "id": key if key is not None else "",
                    "name": value,
                }
            )

        return values
