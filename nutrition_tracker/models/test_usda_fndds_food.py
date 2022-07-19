from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.models import usda_fndds_food
from nutrition_tracker.tests import objects as test_objects


class TestModelsUSDAFnddsFood(TestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.FNDDS_FOOD = test_objects.get_usda_fndds_food()

    def test_empty_qs(self):
        self.assertFalse(usda_fndds_food.empty_qs().exists())

    def test_load_queryset(self):
        self.assertEqual(1, usda_fndds_food._load_queryset().count())

    def test_load_fndds_food_no_params(self):
        self.assertIsNone(usda_fndds_food.load_fndds_food())

    def test_load_fndds_food_fdc_id(self):
        self.assertEqual(self.FNDDS_FOOD, usda_fndds_food.load_fndds_food(fdc_id=self.FNDDS_FOOD.usda_food_id))

    def test_load_fndds_foods_no_params(self):
        self.assertEqual(1, usda_fndds_food.load_fndds_foods().count())

    def test_load_fndds_foods_fdc_ids(self):
        self.assertEqual(1, usda_fndds_food.load_fndds_foods(fdc_ids=[self.FNDDS_FOOD.usda_food_id]).count())

    def test_create(self):
        usda_fndds_food.create(usda_food=test_objects.get_usda_food_2())
        self.assertEqual(2, usda_fndds_food.load_fndds_foods().count())

    def test_update_or_create(self):
        self.assertIsNone(self.FNDDS_FOOD.wweia_category_number)
        usda_fndds_food.update_or_create(defaults={"wweia_category_number": 2}, usda_food=self.FNDDS_FOOD.usda_food)
        self.FNDDS_FOOD.refresh_from_db()
        self.assertEqual(2, self.FNDDS_FOOD.wweia_category_number)

        usda_fndds_food.update_or_create(defaults={"food_code": 3}, usda_food=test_objects.get_usda_food_2())
        self.assertEqual(2, usda_fndds_food.load_fndds_foods().count())
