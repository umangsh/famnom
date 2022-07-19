"""Nutrition values utility methods."""
from __future__ import annotations

from nutrition_tracker.constants import constants


def process_min_threshold_value(value: float | None, default: float = constants.INT_MIN_VALUE) -> int:
    """Values are capped/rounded according to the following rules:
    1. If value is 0 or None, use the default.
    2. Round the value.
    """
    return round(value or default)


def process_max_threshold_value(value: float | None, default: float = constants.INT_MAX_VALUE) -> int:
    """Values are capped/rounded according to the following rules:
    1. If value is 0 or None, use the default.
    2. Round the value.
    """
    return round(value or default)


def process_exact_threshold_value(value: float | None) -> int:
    """Values are capped/rounded according to the following rules:
    1. Round the value.
    """
    return round(value or 0)
