from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.logic import data_loaders
from nutrition_tracker.models import user_meal, user_recipe
from nutrition_tracker.tests import objects as test_objects


class TestLogicDataLoaders(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()

    def test_get_lfood_ids_for_recipe(self):
        lfood = test_objects.get_user_ingredient()
        lfood_2 = test_objects.get_user_ingredient_2()
        lrecipe = test_objects.get_recipe()
        test_objects.get_user_food_membership(lrecipe, lfood)
        test_objects.get_user_food_membership(lrecipe, lfood_2)

        lrecipe = user_recipe.load_lrecipe(self.USER, id_=lrecipe.id)
        self.assertEqual(set({lfood.id, lfood_2.id}), data_loaders.get_lfood_ids_for_lparents(self.USER, [lrecipe]))

    def test_get_lfood_ids_for_meal(self):
        lfood = test_objects.get_user_ingredient()
        lfood_2 = test_objects.get_user_ingredient_2()
        lmeal = test_objects.get_meal_today_1()
        test_objects.get_user_food_membership(lmeal, lfood)
        test_objects.get_user_food_membership(lmeal, lfood_2)

        lmeal = user_meal.load_lmeal(self.USER, id_=lmeal.id)
        self.assertEqual(set({lfood.id, lfood_2.id}), data_loaders.get_lfood_ids_for_lparents(self.USER, [lmeal]))

    def test_load_lfoods_for_recipe(self):
        lfood = test_objects.get_user_ingredient()
        lfood_2 = test_objects.get_user_ingredient_2()
        lrecipe = test_objects.get_recipe()
        test_objects.get_user_food_membership(lrecipe, lfood)
        test_objects.get_user_food_membership(lrecipe, lfood_2)

        lrecipe = user_recipe.load_lrecipe(self.USER, id_=lrecipe.id)
        self.assertQuerysetEqual(
            data_loaders.load_lfoods_for_lparents(self.USER, [lrecipe]), set({lfood, lfood_2}), ordered=False
        )

    def test_load_lfoods_for_recipe_no_food(self):
        lrecipe = test_objects.get_recipe()
        lrecipe = user_recipe.load_lrecipe(self.USER, id_=lrecipe.id)
        self.assertQuerysetEqual(data_loaders.load_lfoods_for_lparents(self.USER, [lrecipe]), set(), ordered=False)

    def test_load_lfoods_for_meal(self):
        lfood = test_objects.get_user_ingredient()
        lfood_2 = test_objects.get_user_ingredient_2()
        lmeal = test_objects.get_meal_today_1()
        test_objects.get_user_food_membership(lmeal, lfood)
        test_objects.get_user_food_membership(lmeal, lfood_2)

        lmeal = user_meal.load_lmeal(self.USER, id_=lmeal.id)
        self.assertQuerysetEqual(
            data_loaders.load_lfoods_for_lparents(self.USER, [lmeal]), set({lfood, lfood_2}), ordered=False
        )

    def test_get_lrecipe_ids_for_recipe(self):
        lrecipe = test_objects.get_recipe()
        lrecipe_2 = test_objects.get_recipe_2()
        test_objects.get_user_food_membership(lrecipe, lrecipe_2)

        lrecipe = user_recipe.load_lrecipe(self.USER, id_=lrecipe.id)
        self.assertEqual(set({lrecipe_2.id}), data_loaders.get_lrecipe_ids_for_lparents(self.USER, [lrecipe]))

    def test_get_lrecipe_ids_for_meal(self):
        lrecipe = test_objects.get_recipe()
        lrecipe_2 = test_objects.get_recipe_2()
        lmeal = test_objects.get_meal_today_1()
        test_objects.get_user_food_membership(lmeal, lrecipe)
        test_objects.get_user_food_membership(lmeal, lrecipe_2)

        lmeal = user_meal.load_lmeal(self.USER, id_=lmeal.id)
        self.assertEqual(
            set({lrecipe.id, lrecipe_2.id}), data_loaders.get_lrecipe_ids_for_lparents(self.USER, [lmeal])
        )

    def test_get_lrecipes_for_recipe(self):
        lrecipe = test_objects.get_recipe()
        lrecipe_2 = test_objects.get_recipe_2()
        test_objects.get_user_food_membership(lrecipe, lrecipe_2)

        lrecipe = user_recipe.load_lrecipe(self.USER, id_=lrecipe.id)
        self.assertQuerysetEqual(
            data_loaders.load_lrecipes_for_lparents(self.USER, [lrecipe]), set({lrecipe_2}), ordered=False
        )

    def test_load_lrecipes_for_recipe_no_recipe(self):
        lrecipe = test_objects.get_recipe()
        lrecipe = user_recipe.load_lrecipe(self.USER, id_=lrecipe.id)
        self.assertQuerysetEqual(data_loaders.load_lrecipes_for_lparents(self.USER, [lrecipe]), set(), ordered=False)

    def test_get_lrecipes_for_meal(self):
        lrecipe = test_objects.get_recipe()
        lrecipe_2 = test_objects.get_recipe_2()
        lmeal = test_objects.get_meal_today_1()
        test_objects.get_user_food_membership(lmeal, lrecipe)
        test_objects.get_user_food_membership(lmeal, lrecipe_2)

        lmeal = user_meal.load_lmeal(self.USER, id_=lmeal.id)
        self.assertQuerysetEqual(
            data_loaders.load_lrecipes_for_lparents(self.USER, [lmeal]), set({lrecipe, lrecipe_2}), ordered=False
        )
