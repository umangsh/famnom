from __future__ import annotations

from unittest.mock import Mock

from django.test import SimpleTestCase
from django.test.client import RequestFactory
from django.utils import timezone

from nutrition_tracker.middleware import TimezoneMiddleware


class TestMiddlewareTimezone(SimpleTestCase):
    def test_timezone(self):
        get_response = Mock()
        request = RequestFactory().get("/")
        request.COOKIES["user_tz"] = "Europe/London"
        TimezoneMiddleware(get_response)(request)
        self.assertEqual(timezone.get_current_timezone_name(), "Europe/London")
