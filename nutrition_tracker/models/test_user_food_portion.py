from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.biz import user
from nutrition_tracker.constants import constants
from nutrition_tracker.logic import data_loaders
from nutrition_tracker.models import user_food_portion
from nutrition_tracker.tests import objects as test_objects


class TestModelsUserFoodPortion(TestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.FOOD_PORTION = test_objects.get_user_food_portion()

    def test_empty_qs(self):
        self.assertFalse(user_food_portion.empty_qs().exists())

    def test_load_queryset(self):
        self.assertEqual(1, user_food_portion._load_queryset(self.FOOD_PORTION.user).count())

    def test_load_queryset_with_family(self):
        luser_2 = test_objects.get_user_2()
        user.create_family(self.USER, luser_2.email)
        luser_2.refresh_from_db()
        self.assertEqual(1, user_food_portion._load_queryset(luser_2).count())

    def test_load_portions_no_params(self):
        user = test_objects.get_user()
        self.assertEqual(1, user_food_portion.load_lfood_portions(user).count())

    def test_load_portions_ids(self):
        user = test_objects.get_user()
        self.assertEqual(1, user_food_portion.load_lfood_portions(user, ids=[self.FOOD_PORTION.id]).count())

    def test_create(self):
        user = test_objects.get_user()
        user_food_portion.create(
            user,
            content_object=test_objects.get_user_ingredient_2(),
            serving_size=50,
            serving_size_unit=constants.ServingSizeUnit.WEIGHT,
        )
        self.assertEqual(2, user_food_portion.load_lfood_portions(user).count())

    def test_update_or_create(self):
        user = test_objects.get_user()
        self.assertEqual(83, self.FOOD_PORTION.serving_size)
        user_food_portion.update_or_create(user, defaults={"serving_size": 200}, id=self.FOOD_PORTION.id)
        self.FOOD_PORTION.refresh_from_db()
        self.assertEqual(200, self.FOOD_PORTION.serving_size)

        ingredient = test_objects.get_user_ingredient_2()
        user_food_portion.update_or_create(
            user,
            defaults={"serving_size": 175, "serving_size_unit": constants.ServingSizeUnit.WEIGHT},
            object_id=ingredient.id,
            content_type=data_loaders.get_content_type_ingredient(),
        )
        self.assertEqual(2, user_food_portion.load_lfood_portions(user).count())
