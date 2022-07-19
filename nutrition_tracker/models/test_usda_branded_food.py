from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.models import usda_branded_food
from nutrition_tracker.tests import objects as test_objects


class TestModelsUSDABrandedFood(TestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.BRANDED_FOOD = test_objects.get_usda_branded_food()

    def test_empty_qs(self):
        self.assertFalse(usda_branded_food.empty_qs().exists())

    def test_load_queryset(self):
        self.assertEqual(1, usda_branded_food._load_queryset().count())

    def test_load_cbranded_food_no_params(self):
        self.assertIsNone(usda_branded_food.load_cbranded_food())

    def test_load_cbranded_food_fdc_id(self):
        self.assertEqual(
            self.BRANDED_FOOD, usda_branded_food.load_cbranded_food(fdc_id=self.BRANDED_FOOD.usda_food_id)
        )

    def test_load_cbranded_foods_no_params(self):
        self.assertEqual(1, usda_branded_food.load_cbranded_foods().count())

    def test_load_cbranded_foods_fdc_ids(self):
        self.assertEqual(1, usda_branded_food.load_cbranded_foods(fdc_ids=[self.BRANDED_FOOD.usda_food_id]).count())

    def test_load_cbranded_foods_upc(self):
        self.assertEqual(1, usda_branded_food.load_cbranded_foods(gtin_upc=self.BRANDED_FOOD.gtin_upc).count())

    def test_load_cbranded_foods_all_params(self):
        self.assertEqual(
            1,
            usda_branded_food.load_cbranded_foods(
                fdc_ids=[self.BRANDED_FOOD.usda_food_id], gtin_upc=self.BRANDED_FOOD.gtin_upc
            ).count(),
        )

    def test_create(self):
        usda_branded_food.create(usda_food=test_objects.get_usda_food_2())
        self.assertEqual(2, usda_branded_food.load_cbranded_foods().count())

    def test_update_or_create(self):
        self.assertIsNone(self.BRANDED_FOOD.subbrand_name)
        usda_branded_food.update_or_create(
            defaults={"subbrand_name": "subbrand"}, usda_food=self.BRANDED_FOOD.usda_food
        )
        self.BRANDED_FOOD.refresh_from_db()
        self.assertEqual("subbrand", self.BRANDED_FOOD.subbrand_name)

        usda_branded_food.update_or_create(defaults={"brand_name": "brand"}, usda_food=test_objects.get_usda_food_2())
        self.assertEqual(2, usda_branded_food.load_cbranded_foods().count())
