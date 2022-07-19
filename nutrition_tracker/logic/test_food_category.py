from __future__ import annotations

from django.test import SimpleTestCase
from django.utils.translation import gettext_lazy as _

from nutrition_tracker.logic import food_category


class TestLogicFoodCategory(SimpleTestCase):
    def test_get_category(self):
        category_id = 3
        self.assertEqual(category_id, food_category.get_category(category_id).id_)

    def test_get_wweia_category(self):
        category_id = 6012
        self.assertEqual(category_id, food_category.get_category(category_id).id_)

    def test_for_display(self):
        category_id = 3
        self.assertEqual("Baby Foods", food_category.for_display(category_id))

    def test_for_display_wweia(self):
        category_id = 6012
        self.assertEqual("Citrus fruits", food_category.for_display(category_id))

    def test_for_display_invalid(self):
        category_id = "INVALID_CATEGORY"
        self.assertIsNone(food_category.for_display(category_id))

    def test_for_display_choices(self):
        choices = food_category.for_display_choices()
        self.assertEqual(choices[0], ("", _("Select Category")))
        other_choices = choices[1:]
        self.assertEqual(other_choices, sorted(other_choices, key=lambda x: x[1]))
