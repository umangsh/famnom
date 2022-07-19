from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.models import usda_foundation_food
from nutrition_tracker.tests import objects as test_objects


class TestModelsUSDAFoundationFood(TestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.FOUNDATION_FOOD = test_objects.get_usda_foundation_food()

    def test_empty_qs(self):
        self.assertFalse(usda_foundation_food.empty_qs().exists())

    def test_load_queryset(self):
        self.assertEqual(1, usda_foundation_food._load_queryset().count())

    def test_load_foundation_food_no_params(self):
        self.assertIsNone(usda_foundation_food.load_foundation_food())

    def test_load_foundation_food_fdc_id(self):
        self.assertEqual(
            self.FOUNDATION_FOOD, usda_foundation_food.load_foundation_food(fdc_id=self.FOUNDATION_FOOD.usda_food_id)
        )

    def test_load_foundation_foods_no_params(self):
        self.assertEqual(1, usda_foundation_food.load_foundation_foods().count())

    def test_load_foundation_foods_fdc_ids(self):
        self.assertEqual(
            1, usda_foundation_food.load_foundation_foods(fdc_ids=[self.FOUNDATION_FOOD.usda_food_id]).count()
        )

    def test_load_foundation_foods_ndb_number(self):
        self.assertEqual(
            1, usda_foundation_food.load_foundation_foods(ndb_number=self.FOUNDATION_FOOD.ndb_number).count()
        )

    def test_create(self):
        usda_foundation_food.create(usda_food=test_objects.get_usda_food_2())
        self.assertEqual(2, usda_foundation_food.load_foundation_foods().count())

    def test_update_or_create(self):
        self.assertIsNone(self.FOUNDATION_FOOD.footnote)
        usda_foundation_food.update_or_create(
            defaults={"footnote": "footnote"}, usda_food=self.FOUNDATION_FOOD.usda_food
        )
        self.FOUNDATION_FOOD.refresh_from_db()
        self.assertEqual("footnote", self.FOUNDATION_FOOD.footnote)

        usda_foundation_food.update_or_create(defaults={"ndb_number": "345"}, usda_food=test_objects.get_usda_food_2())
        self.assertEqual(2, usda_foundation_food.load_foundation_foods().count())
