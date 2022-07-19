"""Timezone middleware."""
from __future__ import annotations

import zoneinfo
from typing import Callable
from urllib.parse import unquote

from django.http import HttpRequest, HttpResponse
from django.utils import timezone


class TimezoneMiddleware:  # pylint: disable=too-few-public-methods
    """
    Middleware to properly handle the users timezone
    """

    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # we are getting the users timezone from the cookie
        tz_str: str | None = request.COOKIES.get("user_tz")
        if tz_str:
            tz_str = unquote(tz_str)
            timezone.activate(zoneinfo.ZoneInfo(tz_str))
        else:
            timezone.deactivate()

        return self.get_response(request)
