from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.biz import user
from nutrition_tracker.constants import constants
from nutrition_tracker.models import user_food_nutrient
from nutrition_tracker.tests import objects as test_objects


class TestModelsUserFoodNutrient(TestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.FOOD_NUTRIENT = test_objects.get_user_food_nutrient()

    def test_empty_qs(self):
        self.assertFalse(user_food_nutrient.empty_qs().exists())

    def test_load_queryset(self):
        self.assertEqual(1, user_food_nutrient._load_queryset(self.USER).count())

    def test_load_nutrients_no_params(self):
        self.assertEqual(1, user_food_nutrient.load_nutrients(self.USER).count())

    def test_load_queryset_with_family(self):
        luser_2 = test_objects.get_user_2()
        user.create_family(self.USER, luser_2.email)
        luser_2.refresh_from_db()
        self.assertEqual(1, user_food_nutrient.load_nutrients(luser_2).count())

    def test_load_nutrients_ids(self):
        self.assertEqual(1, user_food_nutrient.load_nutrients(self.USER, ids=[self.FOOD_NUTRIENT.id]).count())

    def test_load_nutrients_ingredients(self):
        self.assertEqual(
            1, user_food_nutrient.load_nutrients(self.USER, ingredients=[self.FOOD_NUTRIENT.ingredient]).count()
        )

    def test_load_nutrients_nutrient_ids(self):
        self.assertEqual(
            1, user_food_nutrient.load_nutrients(self.USER, nutrient_ids=[constants.ENERGY_NUTRIENT_ID]).count()
        )

    def test_create(self):
        user_food_nutrient.create(self.USER, ingredient=test_objects.get_user_ingredient_2())
        self.assertEqual(2, user_food_nutrient.load_nutrients(self.USER).count())

    def test_update_or_create(self):
        self.assertEqual(100, self.FOOD_NUTRIENT.amount)
        user_food_nutrient.update_or_create(self.USER, defaults={"amount": 200}, id=self.FOOD_NUTRIENT.id)
        self.FOOD_NUTRIENT.refresh_from_db()
        self.assertEqual(200, self.FOOD_NUTRIENT.amount)

        user_food_nutrient.update_or_create(
            self.USER,
            defaults={"nutrient_id": constants.ENERGY_NUTRIENT_ID, "amount": 150},
            ingredient=test_objects.get_user_ingredient_2(),
        )
        self.assertEqual(2, user_food_nutrient.load_nutrients(self.USER).count())
