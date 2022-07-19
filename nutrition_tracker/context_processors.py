"""Custom context processors."""
from __future__ import annotations

from typing import Any

from django.http import HttpRequest

from nutrition_tracker.constants import constants


def add_constants(request: HttpRequest) -> dict[str, Any]:
    """Make constants available to templates."""
    kwargs: dict[str, Any] = {}
    for item in dir(constants):
        if not item.startswith("__"):
            kwargs[item] = getattr(constants, item)
    return kwargs
