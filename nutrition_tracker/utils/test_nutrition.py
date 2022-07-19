from __future__ import annotations

from django.test import SimpleTestCase

from nutrition_tracker.constants import constants
from nutrition_tracker.utils import nutrition


class TestUtilsNutrition(SimpleTestCase):
    def test_process_min_threshold_value_default(self):
        self.assertEqual(constants.INT_MIN_VALUE, nutrition.process_min_threshold_value(0.0))

    def test_process_min_threshold_value(self):
        self.assertEqual(1, nutrition.process_min_threshold_value(0.95))

    def test_process_max_threshold_value_default(self):
        self.assertEqual(constants.INT_MAX_VALUE, nutrition.process_max_threshold_value(0.0))

    def test_process_max_threshold_value(self):
        self.assertEqual(1, nutrition.process_max_threshold_value(0.95))

    def test_process_exact_threshold_value(self):
        self.assertEqual(1, nutrition.process_exact_threshold_value(0.95))
