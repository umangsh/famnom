"""Utility methods for DB models."""
from __future__ import annotations

from typing import Any

from nutrition_tracker.constants import constants
from nutrition_tracker.models import user_meal


def get_field_names(
    field_list: list[Any], prefix_fields_in_order: list[Any] | None = None, skip_fields: list[Any] | None = None
) -> list[Any]:
    """Filter/order field_list based on input parameters. Fields in prefix_fields_in_order are ordered first, and fields in skip_fields are skipped.

    For e.g.
    field_list: [1,2,3,4]
    prefix_fields_in_order: [3,1]
    skip_fields: [2]

    Returns: [3,1,4]
    """
    if not prefix_fields_in_order:
        prefix_fields_in_order = []
    if skip_fields is None:
        skip_fields = ["id", "created_timestamp", "updated_timestamp"]

    return prefix_fields_in_order + [
        f.name for f in field_list if f.name not in skip_fields and f.name not in prefix_fields_in_order
    ]


def sort_meals(lmeals: list[user_meal.UserMeal], reverse: bool = False) -> list[user_meal.UserMeal]:
    """Sort meals by meal date and meal type."""
    return sorted(
        lmeals,
        key=(lambda x: (x.meal_date, list(zip(*constants.MealType.choices))[0].index(x.meal_type))),
        reverse=reverse,
    )
