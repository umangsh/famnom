"""URL Factory: URL generation / manipulation library."""
from __future__ import annotations

import urllib.parse
from typing import Any
from uuid import UUID

from nutrition_tracker.constants import constants


def get_url(path: str, **kwargs: Any) -> str:
    """Get URL string for path and URL args."""
    if not kwargs:
        return path

    return f"{path}?{urllib.parse.urlencode(kwargs)}"


def get_ingredient_url(external_id: str | UUID, **kwargs: str) -> str:
    """Get ingredient URL."""
    base_url = f"/{constants.URL_DETAIL_INGREDIENT}/{external_id}/"
    return get_url(base_url, **kwargs)


def get_food_url(external_id: str | UUID, **kwargs: str) -> str:
    """Get cfood (DBFood) URL."""
    base_url = f"/{constants.URL_DETAIL_FOOD}/{external_id}/"
    return get_url(base_url, **kwargs)
