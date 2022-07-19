"""Forms/fields processing methods."""
from __future__ import annotations

import uuid


def get_field_name(item_id: int | str | uuid.UUID) -> str:
    """Return a string field name corresponding to input
    item_id. Used by FE form handling."""
    return f"{item_id}"


def get_threshold_field_name(item_id: int | str | uuid.UUID) -> str:
    """Return a string field name corresponding to input
    item_id. Used by FE form handling for threshold fields."""
    return f"threshold_{item_id}"


def get_meal_field_name(item_id: int | str | uuid.UUID) -> str:
    """Return a string field name corresponding to input
    item_id. Used by FE form handling for meal fields."""
    return f"meal_{item_id}"
