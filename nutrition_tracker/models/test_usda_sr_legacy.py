from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.models import usda_sr_legacy
from nutrition_tracker.tests import objects as test_objects


class TestModelsUSDASRLegacyFood(TestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.SR_LEGACY_FOOD = test_objects.get_usda_sr_legacy_food()

    def test_empty_qs(self):
        self.assertFalse(usda_sr_legacy.empty_qs().exists())

    def test_load_queryset(self):
        self.assertEqual(1, usda_sr_legacy._load_queryset().count())

    def test_load_sr_legacy_food_no_params(self):
        self.assertIsNone(usda_sr_legacy.load_sr_legacy_food())

    def test_load_sr_legacy_food_fdc_id(self):
        self.assertEqual(
            self.SR_LEGACY_FOOD, usda_sr_legacy.load_sr_legacy_food(fdc_id=self.SR_LEGACY_FOOD.usda_food_id)
        )

    def test_load_sr_legacy_foods_no_params(self):
        self.assertEqual(1, usda_sr_legacy.load_sr_legacy_foods().count())

    def test_load_sr_legacy_foods_fdc_ids(self):
        self.assertEqual(1, usda_sr_legacy.load_sr_legacy_foods(fdc_ids=[self.SR_LEGACY_FOOD.usda_food_id]).count())

    def test_load_sr_legacy_foods_ndb_number(self):
        self.assertEqual(1, usda_sr_legacy.load_sr_legacy_foods(ndb_number=self.SR_LEGACY_FOOD.ndb_number).count())

    def test_create(self):
        usda_sr_legacy.create(usda_food=test_objects.get_usda_food_2())
        self.assertEqual(2, usda_sr_legacy.load_sr_legacy_foods().count())

    def test_update_or_create(self):
        self.assertEqual("123", self.SR_LEGACY_FOOD.ndb_number)
        usda_sr_legacy.update_or_create(defaults={"ndb_number": "345"}, usda_food=self.SR_LEGACY_FOOD.usda_food)
        self.SR_LEGACY_FOOD.refresh_from_db()
        self.assertEqual("345", self.SR_LEGACY_FOOD.ndb_number)

        usda_sr_legacy.update_or_create(defaults={"ndb_number": "789"}, usda_food=test_objects.get_usda_food_2())
        self.assertEqual(2, usda_sr_legacy.load_sr_legacy_foods().count())
