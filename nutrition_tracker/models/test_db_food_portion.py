from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.models import db_food_portion
from nutrition_tracker.tests import objects as test_objects


class TestModelsDBFoodPortion(TestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.FOOD_PORTION = test_objects.get_db_food_portion()

    def test_empty_qs(self):
        self.assertFalse(db_food_portion.empty_qs().exists())

    def test_load_queryset(self):
        self.assertEqual(1, db_food_portion._load_queryset().count())

    def test_load_portion_no_params(self):
        self.assertIsNone(db_food_portion.load_portion())

    def test_load_portion_id(self):
        self.assertEqual(self.FOOD_PORTION, db_food_portion.load_portion(id_=self.FOOD_PORTION.id))

    def test_load_portion_external_id(self):
        self.assertEqual(self.FOOD_PORTION, db_food_portion.load_portion(external_id=self.FOOD_PORTION.external_id))

    def test_load_portions_no_params(self):
        self.assertEqual(1, db_food_portion.load_portions().count())

    def test_load_portions_ids(self):
        self.assertEqual(1, db_food_portion.load_portions(ids=[self.FOOD_PORTION.id]).count())

    def test_load_portions_external_ids(self):
        self.assertEqual(1, db_food_portion.load_portions(external_ids=[self.FOOD_PORTION.external_id]).count())

    def test_load_portions_db_food_ids(self):
        self.assertEqual(1, db_food_portion.load_portions(db_food_ids=[self.FOOD_PORTION.db_food_id]).count())

    def test_create(self):
        db_food_portion.create(id=3, db_food=test_objects.get_db_food_2())
        self.assertEqual(2, db_food_portion.load_portions().count())

    def test_update_or_create(self):
        self.assertIsNone(self.FOOD_PORTION.portion_description)
        db_food_portion.update_or_create(defaults={"portion_description": "description"}, id=self.FOOD_PORTION.id)
        self.FOOD_PORTION.refresh_from_db()
        self.assertEqual("description", self.FOOD_PORTION.portion_description)

        db_food_portion.update_or_create(
            defaults={"portion_description": "description"}, id=2, db_food=test_objects.get_db_food()
        )
        self.assertEqual(2, db_food_portion.load_portions().count())
