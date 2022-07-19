from __future__ import annotations

from django.test import SimpleTestCase

from nutrition_tracker.forms import SearchForm


class TestFormsSearchForm(SimpleTestCase):
    def test_valid_query(self):
        form = SearchForm(data={"q": "test"})
        self.assertTrue(form.is_valid())
