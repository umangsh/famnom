from __future__ import annotations

from django.test import SimpleTestCase

from nutrition_tracker.utils import form


class TestUtilsForm(SimpleTestCase):
    def test_get_field_name(self):
        item_id = 123
        expected_output = "123"
        self.assertEqual(expected_output, form.get_field_name(item_id))

    def test_get_threshold_field_name(self):
        item_id = 123
        expected_output = "threshold_123"
        self.assertEqual(expected_output, form.get_threshold_field_name(item_id))

    def test_get_meal_field_name(self):
        item_id = 123
        expected_output = "meal_123"
        self.assertEqual(expected_output, form.get_meal_field_name(item_id))
