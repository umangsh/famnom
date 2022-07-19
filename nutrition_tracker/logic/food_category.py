"""Food category logic module."""
from __future__ import annotations

from typing import Iterable, Sequence

from django.utils.translation import gettext_lazy as _

from nutrition_tracker.config import usda_config
from nutrition_tracker.constants import constants


def get_category(category_id: int) -> usda_config.USDAFoodCategory | usda_config.WWEIAFoodCategory | None:
    """Get category from ID."""
    category: usda_config.USDAFoodCategory | usda_config.WWEIAFoodCategory | None = next(
        (category for category in usda_config.usda_food_categories if category.id_ == category_id), None
    )

    if not category:
        # Sometimes, category_id can include wweia_food_category.
        # For e.g. Lemon, raw
        category = next(
            (category for category in usda_config.wweia_food_categories if category.id_ == category_id), None
        )

    return category


def for_display(category_id: int) -> str | None:
    """Formatted category name for display."""
    category = get_category(category_id)

    if not category:
        return None

    return category.description


def for_display_choices() -> Sequence[tuple[str, str]]:
    """Formatted category choices for display."""
    _choices: Iterable[tuple[str, str]] = [
        (str(category.id_), category.description)
        for category in usda_config.usda_food_categories
        if category.id_ != constants.CATEGORY_ALL_FOODS
    ]
    choices: Sequence[tuple[str, str]] = [("", _("Select Category"))] + sorted(_choices, key=lambda x: x[1])

    return choices
