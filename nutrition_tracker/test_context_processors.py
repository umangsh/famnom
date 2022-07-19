from __future__ import annotations

from django.test import SimpleTestCase
from django.test.client import RequestFactory

from nutrition_tracker import context_processors


class TestContextProcessors(SimpleTestCase):
    def test_add_constants(self):
        request = RequestFactory().get("/")
        kwargs = context_processors.add_constants(request)
        self.assertTrue("USDA_FOUNDATION_FOOD" in kwargs)
