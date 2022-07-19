from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.constants import constants
from nutrition_tracker.models import db_food_nutrient
from nutrition_tracker.tests import objects as test_objects


class TestModelsDBFoodNutrient(TestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.FOOD_NUTRIENT = test_objects.get_db_food_nutrient()

    def test_empty_qs(self):
        self.assertFalse(db_food_nutrient.empty_qs().exists())

    def test_load_queryset(self):
        self.assertEqual(1, db_food_nutrient._load_queryset().count())

    def test_load_nutrient_no_params(self):
        self.assertIsNone(db_food_nutrient.load_nutrient())

    def test_load_nutrient_id(self):
        self.assertEqual(self.FOOD_NUTRIENT, db_food_nutrient.load_nutrient(id_=self.FOOD_NUTRIENT.id))

    def test_load_nutrients_no_params(self):
        self.assertEqual(1, db_food_nutrient.load_nutrients().count())

    def test_load_nutrients_ids(self):
        self.assertEqual(1, db_food_nutrient.load_nutrients(ids=[self.FOOD_NUTRIENT.id]).count())

    def test_load_nutrients_db_food_ids(self):
        self.assertEqual(1, db_food_nutrient.load_nutrients(db_food_ids=[self.FOOD_NUTRIENT.db_food_id]).count())

    def test_load_nutrients_nutrient_id(self):
        self.assertEqual(1, db_food_nutrient.load_nutrients(nutrient_ids=[constants.ENERGY_NUTRIENT_ID]).count())

    def test_load_nutrients_nutrient_id_db_source_sub_types(self):
        self.assertEqual(
            1,
            db_food_nutrient.load_nutrients(
                db_source_types=[constants.DBFoodSourceType.USDA],
                db_source_sub_types=[constants.DBFoodSourceSubType.USDA_BRANDED_FOOD],
                nutrient_ids=[constants.ENERGY_NUTRIENT_ID],
            ).count(),
        )

    def test_load_nutrients_nutrient_id_db_source_sub_types_not_found(self):
        self.assertEqual(
            0,
            db_food_nutrient.load_nutrients(
                db_source_types=[constants.DBFoodSourceType.USDA],
                db_source_sub_types=[constants.DBFoodSourceSubType.USDA_FOUNDATION_FOOD],
                nutrient_ids=[constants.ENERGY_NUTRIENT_ID],
            ).count(),
        )

    def test_create(self):
        db_food_nutrient.create(
            id=3, db_food=test_objects.get_db_food_2(), nutrient_id=constants.ENERGY_NUTRIENT_ID, amount=50
        )
        self.assertEqual(2, db_food_nutrient.load_nutrients().count())

    def test_update_or_create(self):
        self.assertEqual(100, self.FOOD_NUTRIENT.amount)
        db_food_nutrient.update_or_create(defaults={"amount": 12}, id=self.FOOD_NUTRIENT.id)
        self.FOOD_NUTRIENT.refresh_from_db()
        self.assertEqual(12, self.FOOD_NUTRIENT.amount)

        db_food_nutrient.update_or_create(
            defaults={"amount": 23},
            id=2,
            db_food=test_objects.get_db_food(),
            nutrient_id=constants.PROTEIN_NUTRIENT_ID,
        )
        self.assertEqual(2, db_food_nutrient.load_nutrients().count())
