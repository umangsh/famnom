from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.constants import constants
from nutrition_tracker.models import usda_food_nutrient
from nutrition_tracker.tests import objects as test_objects


class TestModelsUSDAFoodNutrient(TestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.FOOD_NUTRIENT = test_objects.get_usda_food_nutrient()

    def test_empty_qs(self):
        self.assertFalse(usda_food_nutrient.empty_qs().exists())

    def test_load_queryset(self):
        self.assertEqual(1, usda_food_nutrient._load_queryset().count())

    def test_load_nutrient_no_params(self):
        self.assertIsNone(usda_food_nutrient.load_nutrient())

    def test_load_nutrient_id(self):
        self.assertEqual(self.FOOD_NUTRIENT, usda_food_nutrient.load_nutrient(id_=self.FOOD_NUTRIENT.id))

    def test_load_nutrients_no_params(self):
        self.assertEqual(1, usda_food_nutrient.load_nutrients().count())

    def test_load_nutrients_ids(self):
        self.assertEqual(1, usda_food_nutrient.load_nutrients(ids=[self.FOOD_NUTRIENT.id]).count())

    def test_load_nutrients_fdc_ids(self):
        self.assertEqual(1, usda_food_nutrient.load_nutrients(fdc_ids=[self.FOOD_NUTRIENT.usda_food_id]).count())

    def test_load_nutrients_nutrient_id(self):
        self.assertEqual(1, usda_food_nutrient.load_nutrients(nutrient_ids=[constants.ENERGY_NUTRIENT_ID]).count())

    def test_load_nutrients_nutrient_id_food_types(self):
        self.assertEqual(
            1,
            usda_food_nutrient.load_nutrients(
                food_types=[constants.USDA_BRANDED_FOOD], nutrient_ids=[constants.ENERGY_NUTRIENT_ID]
            ).count(),
        )

    def test_load_nutrients_nutrient_id_food_types_not_found(self):
        self.assertEqual(
            0,
            usda_food_nutrient.load_nutrients(
                food_types=[constants.USDA_FOUNDATION_FOOD], nutrient_ids=[constants.ENERGY_NUTRIENT_ID]
            ).count(),
        )

    def test_create(self):
        usda_food_nutrient.create(
            id=3, usda_food=test_objects.get_usda_food_2(), nutrient_id=constants.ENERGY_NUTRIENT_ID, amount=50
        )
        self.assertEqual(2, usda_food_nutrient.load_nutrients().count())

    def test_update_or_create(self):
        self.assertIsNone(self.FOOD_NUTRIENT.data_points)
        usda_food_nutrient.update_or_create(defaults={"data_points": 12}, id=self.FOOD_NUTRIENT.id)
        self.FOOD_NUTRIENT.refresh_from_db()
        self.assertEqual(12, self.FOOD_NUTRIENT.data_points)

        usda_food_nutrient.update_or_create(
            defaults={"data_points": 23},
            id=2,
            usda_food=test_objects.get_usda_food(),
            nutrient_id=constants.PROTEIN_NUTRIENT_ID,
            amount=10,
        )
        self.assertEqual(2, usda_food_nutrient.load_nutrients().count())
