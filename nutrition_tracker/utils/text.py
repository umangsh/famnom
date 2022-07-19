"""Text utility methods."""
from __future__ import annotations

import datetime
from typing import Any
from uuid import UUID

from django.template import defaultfilters
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from nutrition_tracker.constants import constants


def title(string: str) -> str:
    """Capitalize each word in the input string."""
    if not string:
        return string

    words: list[str] = string.split(" ")
    return " ".join([word.capitalize() for word in words])


def format_date(value: datetime.date | None) -> str:
    """Returns human readable string for input date.

    For e.g. assuming today's date is 24th Dec 2021:
    value = 24th Dec 2021 => 'Today'
    value = 25th Dec 2021 => 'Tomorrow'
    value = 23rd Dec 2021 => 'Yesterday'
    Other values => defaultfilters.date(value)
    """
    if not value:
        return ""

    today: datetime.date = timezone.localdate()
    delta: datetime.timedelta = value - today
    if delta.days == 0:
        result = _("Today")
    elif delta.days == 1:
        result = _("Tomorrow")
    elif delta.days == -1:
        result = _("Yesterday")
    else:
        result = defaultfilters.date(value, constants.DISPLAY_DATE_FORMAT)

    return result


def is_valid_uuid(string: str, version: int = 4) -> bool:
    """Validates input string as valid UUID."""
    try:
        uuid: UUID = UUID(string, version=version)
    except ValueError:
        return False

    return str(uuid) == string


def valid_float(number: Any) -> float | None:
    """Validates input number as valid float."""
    try:
        return float(number)
    except ValueError:
        return None
