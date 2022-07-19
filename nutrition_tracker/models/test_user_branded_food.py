from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.biz import user
from nutrition_tracker.models import user_branded_food
from nutrition_tracker.tests import objects as test_objects


class TestModelsUserBrandedFood(TestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.BRANDED_FOOD = test_objects.get_user_branded_food()

    def test_empty_qs(self):
        self.assertFalse(user_branded_food.empty_qs().exists())

    def test_load_queryset(self):
        self.assertEqual(1, user_branded_food._load_queryset(self.BRANDED_FOOD.user).count())

    def test_load_queryset_with_family(self):
        luser_2 = test_objects.get_user_2()
        user.create_family(self.USER, luser_2.email)
        self.USER.refresh_from_db()
        luser_2.refresh_from_db()

        test_objects.get_user_2_branded_food()
        self.assertEqual(2, user_branded_food._load_queryset(self.USER).count())
        self.assertEqual(2, user_branded_food._load_queryset(luser_2).count())

    def test_load_lbranded_food_no_params(self):
        self.assertIsNone(user_branded_food.load_lbranded_food(self.BRANDED_FOOD.user))

    def test_load_lbranded_food_id(self):
        self.assertEqual(
            self.BRANDED_FOOD, user_branded_food.load_lbranded_food(self.BRANDED_FOOD.user, id_=self.BRANDED_FOOD.id)
        )

    def test_load_lbranded_food_ingredient_id(self):
        self.assertEqual(
            self.BRANDED_FOOD,
            user_branded_food.load_lbranded_food(
                self.BRANDED_FOOD.user, ingredient_id=self.BRANDED_FOOD.ingredient.id
            ),
        )

    def test_load_lbranded_food_gtin_upc(self):
        self.assertEqual(
            self.BRANDED_FOOD,
            user_branded_food.load_lbranded_food(self.BRANDED_FOOD.user, gtin_upc=self.BRANDED_FOOD.gtin_upc),
        )

    def test_load_lbranded_foods_no_params(self):
        user = test_objects.get_user()
        self.assertEqual(1, user_branded_food.load_lbranded_foods(user).count())

    def test_load_lbranded_foods_fdc_ids(self):
        user = test_objects.get_user()
        self.assertEqual(1, user_branded_food.load_lbranded_foods(user, ids=[self.BRANDED_FOOD.id]).count())

    def test_load_lbranded_foods_upc(self):
        user = test_objects.get_user()
        self.assertEqual(
            1, user_branded_food.load_lbranded_foods(user, ingredient_ids=[self.BRANDED_FOOD.ingredient.id]).count()
        )

    def test_load_lbranded_foods_all_params(self):
        user = test_objects.get_user()
        self.assertEqual(
            1, user_branded_food.load_lbranded_foods(user, gtin_upcs=[self.BRANDED_FOOD.gtin_upc]).count()
        )

    def test_create(self):
        user = test_objects.get_user()
        user_branded_food.create(user, ingredient=test_objects.get_user_ingredient_2())
        self.assertEqual(2, user_branded_food.load_lbranded_foods(user).count())

    def test_update_or_create(self):
        user = test_objects.get_user()
        self.assertIsNone(self.BRANDED_FOOD.subbrand_name)
        user_branded_food.update_or_create(user, defaults={"subbrand_name": "subbrand"}, id=self.BRANDED_FOOD.id)
        self.BRANDED_FOOD.refresh_from_db()
        self.assertEqual("subbrand", self.BRANDED_FOOD.subbrand_name)

        user_branded_food.update_or_create(
            user, defaults={"brand_name": "brand"}, ingredient=test_objects.get_user_ingredient_2()
        )
        self.assertEqual(2, user_branded_food.load_lbranded_foods(user).count())
