from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.models import db_branded_food
from nutrition_tracker.tests import objects as test_objects


class TestModelsDBBrandedFood(TestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.BRANDED_FOOD = test_objects.get_db_branded_food()

    def test_empty_qs(self):
        self.assertFalse(db_branded_food.empty_qs().exists())

    def test_load_queryset(self):
        self.assertEqual(1, db_branded_food._load_queryset().count())

    def test_load_cbranded_food_no_params(self):
        self.assertIsNone(db_branded_food.load_cbranded_food())

    def test_load_cbranded_food_db_food_id(self):
        self.assertEqual(
            self.BRANDED_FOOD, db_branded_food.load_cbranded_food(db_food_id=self.BRANDED_FOOD.db_food_id)
        )

    def test_load_cbranded_foods_no_params(self):
        self.assertEqual(1, db_branded_food.load_cbranded_foods().count())

    def test_load_cbranded_foods_db_food_ids(self):
        self.assertEqual(1, db_branded_food.load_cbranded_foods(db_food_ids=[self.BRANDED_FOOD.db_food_id]).count())

    def test_load_cbranded_foods_upc(self):
        self.assertEqual(1, db_branded_food.load_cbranded_foods(gtin_upc=self.BRANDED_FOOD.gtin_upc).count())

    def test_load_cbranded_foods_all_params(self):
        self.assertEqual(
            1,
            db_branded_food.load_cbranded_foods(
                db_food_ids=[self.BRANDED_FOOD.db_food_id], gtin_upc=self.BRANDED_FOOD.gtin_upc
            ).count(),
        )

    def test_create(self):
        db_branded_food.create(db_food=test_objects.get_db_food_2())
        self.assertEqual(2, db_branded_food.load_cbranded_foods().count())

    def test_update_or_create(self):
        self.assertIsNone(self.BRANDED_FOOD.subbrand_name)
        db_branded_food.update_or_create(defaults={"subbrand_name": "subbrand"}, db_food=self.BRANDED_FOOD.db_food)
        self.BRANDED_FOOD.refresh_from_db()
        self.assertEqual("subbrand", self.BRANDED_FOOD.subbrand_name)

        db_branded_food.update_or_create(defaults={"brand_name": "brand"}, db_food=test_objects.get_db_food_2())
        self.assertEqual(2, db_branded_food.load_cbranded_foods().count())
