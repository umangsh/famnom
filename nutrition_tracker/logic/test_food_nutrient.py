from __future__ import annotations

from unittest.mock import patch

from django.test import SimpleTestCase, TestCase

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import data_loaders, food_nutrient, user_prefs
from nutrition_tracker.models import user_ingredient, user_recipe
from nutrition_tracker.tests import objects as test_objects

INVALID_NUTRIENT_ID = 11001100


class TestLogicFoodNutrientGetNutrient(SimpleTestCase):
    def test_nutrient_id(self):
        self.assertEqual(constants.ENERGY_NUTRIENT_ID, food_nutrient.get_nutrient(constants.ENERGY_NUTRIENT_ID).id_)

    def test_nutrient_nbr(self):
        self.assertEqual(constants.ENERGY_NUTRIENT_ID, food_nutrient.get_nutrient(208).id_)

    def test_nutrient_not_found(self):
        self.assertIsNone(food_nutrient.get_nutrient(INVALID_NUTRIENT_ID))


class TestLogicFoodNutrientGetNutrients(SimpleTestCase):
    def test_empty(self):
        self.assertEqual([], food_nutrient.get_nutrients([]))

    def test_valid(self):
        self.assertEqual(1, len(food_nutrient.get_nutrients([constants.ENERGY_NUTRIENT_ID])))

    def test_invalid(self):
        self.assertEqual([], food_nutrient.get_nutrients([INVALID_NUTRIENT_ID]))

    def test_mixed(self):
        self.assertEqual(1, len(food_nutrient.get_nutrients([constants.ENERGY_NUTRIENT_ID, INVALID_NUTRIENT_ID])))


class TestLogicFoodNutrientForDisplay(SimpleTestCase):
    def test_valid(self):
        self.assertEqual("Calories", food_nutrient.for_display(constants.ENERGY_NUTRIENT_ID))

    def test_invalid(self):
        self.assertIsNone(food_nutrient.for_display(INVALID_NUTRIENT_ID))


class TestLogicFoodNutrientForDisplayUnit(SimpleTestCase):
    def test_valid(self):
        self.assertEqual("kcal", food_nutrient.for_display_unit(constants.ENERGY_NUTRIENT_ID))

    def test_valid_alternate_unit(self):
        self.assertEqual("mcg", food_nutrient.for_display_unit(constants.VITAMIN_A_NUTRIENT_ID))

    def test_invalid(self):
        self.assertEqual("", food_nutrient.for_display_unit(INVALID_NUTRIENT_ID))


class TestLogicFoodNutrientGetFdaRdi(SimpleTestCase):
    def test_valid(self):
        return_value = food_nutrient.get_fda_rdi(constants.ENERGY_NUTRIENT_ID)
        self.assertEqual(2000, return_value.adult)

    def test_invalid(self):
        return_value = food_nutrient.get_fda_rdi(INVALID_NUTRIENT_ID)
        self.assertIsNone(return_value)


class TestLogicFoodNutrientGetRdiAmount(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()

    def test_default_value(self):
        preferences = user_prefs.load_nutrition_preferences(self.USER)
        self.assertEqual(2000, food_nutrient.get_rdi_amount(preferences, constants.ENERGY_NUTRIENT_ID))

    def test_preference_value(self):
        test_objects.get_nutrient_preference()
        preferences = user_prefs.load_nutrition_preferences(self.USER)
        self.assertEqual(1000, food_nutrient.get_rdi_amount(preferences, constants.ENERGY_NUTRIENT_ID))

    def test_default_value_with_preferences(self):
        preferences = user_prefs.load_nutrition_preferences(self.USER)
        self.assertEqual(78, food_nutrient.get_rdi_amount(preferences, constants.FAT_NUTRIENT_ID))

    def test_invalid_value(self):
        preferences = user_prefs.load_nutrition_preferences(self.USER)
        self.assertIsNone(food_nutrient.get_rdi_amount(preferences, INVALID_NUTRIENT_ID))


class TestLogicFoodGetAllAliasesForNutrientId(SimpleTestCase):
    def test_valid(self):
        self.assertEqual(
            [1008, 208, 2048, 958, 2047, 957],
            food_nutrient.get_all_aliases_for_nutrient_id(constants.ENERGY_NUTRIENT_ID),
        )

    def test_invalid(self):
        self.assertEqual([], food_nutrient.get_all_aliases_for_nutrient_id(INVALID_NUTRIENT_ID))


class TestLogicFoodGetAllAliasesForNutrientIds(SimpleTestCase):
    def test_valid(self):
        self.assertEqual(
            [1008, 208, 2048, 958, 2047, 957, 1004, 204],
            food_nutrient.get_all_aliases_for_nutrient_ids([constants.ENERGY_NUTRIENT_ID, constants.FAT_NUTRIENT_ID]),
        )

    def test_invalid(self):
        self.assertEqual([], food_nutrient.get_all_aliases_for_nutrient_ids([INVALID_NUTRIENT_ID]))

    def test_mixed(self):
        self.assertEqual(
            [1008, 208, 2048, 958, 2047, 957],
            food_nutrient.get_all_aliases_for_nutrient_ids([constants.ENERGY_NUTRIENT_ID, INVALID_NUTRIENT_ID]),
        )


class TestLogicFoodNutrientGetNutrientAmount(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.USER_FOOD = test_objects.get_user_ingredient()
        test_objects.get_user_food_nutrient()

    def test_valid(self):
        lfood = user_ingredient.load_lfood(self.USER, id_=self.USER_FOOD.id)
        food_nutrients = food_nutrient.get_food_nutrients(lfood, lfood.db_food)
        self.assertEqual(100, food_nutrient.get_nutrient_amount(food_nutrients, constants.ENERGY_NUTRIENT_ID))

    def test_invalid(self):
        lfood = user_ingredient.load_lfood(self.USER, id_=self.USER_FOOD.id)
        food_nutrients = food_nutrient.get_food_nutrients(lfood, lfood.db_food)
        self.assertIsNone(food_nutrient.get_nutrient_amount(food_nutrients, INVALID_NUTRIENT_ID))

    def test_unavailable_nutrient(self):
        lfood = user_ingredient.load_lfood(self.USER, id_=self.USER_FOOD.id)
        food_nutrients = food_nutrient.get_food_nutrients(lfood, lfood.db_food)
        self.assertIsNone(food_nutrient.get_nutrient_amount(food_nutrients, constants.FAT_NUTRIENT_ID))


class TestLogicFoodNutrientGetFoodNutrients(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.USER_FOOD = test_objects.get_user_ingredient()
        test_objects.get_user_food_nutrient()
        test_objects.get_db_food_nutrient()

    def test_lfood(self):
        lfood = user_ingredient.load_lfood(self.USER, id_=self.USER_FOOD.id)
        self.assertEqual(1, len(food_nutrient.get_food_nutrients(lfood, lfood.db_food)))

    def test_cfood(self):
        cfood_2 = test_objects.get_db_food_2()
        self.assertEqual(0, len(food_nutrient.get_food_nutrients(None, cfood_2)))


class TestLogicFoodNutrientGetFoodsNutrients(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.USER_FOOD = test_objects.get_user_ingredient()
        test_objects.get_user_ingredient_2()
        test_objects.get_user_food_nutrient()
        test_objects.get_db_food_nutrient()

    def test_lfoods(self):
        lfoods = user_ingredient.load_lfoods(self.USER)
        self.assertEqual(1, len(food_nutrient.get_foods_nutrients(self.USER, lfoods)))

    def test_lfoods_with_nutrient_id(self):
        lfoods = user_ingredient.load_lfoods(self.USER)
        self.assertEqual(
            1, len(food_nutrient.get_foods_nutrients(self.USER, lfoods, nutrient_id=constants.ENERGY_NUTRIENT_ID))
        )

    def test_lfoods_with_nutrient_id_not_present(self):
        lfoods = user_ingredient.load_lfoods(self.USER)
        self.assertEqual(
            0, len(food_nutrient.get_foods_nutrients(self.USER, lfoods, nutrient_id=constants.PROTEIN_NUTRIENT_ID))
        )


class TestLogicFoodNutrientGetNutrientAmountInFoods(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.USER_FOOD = test_objects.get_user_ingredient()
        test_objects.get_user_ingredient_2()
        test_objects.get_user_food_nutrient()
        test_objects.get_db_food_nutrient()

    def test_nutrient(self):
        lfoods = user_ingredient.load_lfoods(self.USER)
        lfoods_nutrients = food_nutrient.get_foods_nutrients(self.USER, lfoods)
        self.assertEqual(
            100, food_nutrient.get_nutrient_amount_in_foods(lfoods, lfoods_nutrients, constants.ENERGY_NUTRIENT_ID)
        )

    def test_unavailable_nutrient(self):
        lfoods = user_ingredient.load_lfoods(self.USER)
        lfoods_nutrients = food_nutrient.get_foods_nutrients(self.USER, lfoods)
        self.assertIsNone(
            food_nutrient.get_nutrient_amount_in_foods(lfoods, lfoods_nutrients, constants.FAT_NUTRIENT_ID)
        )

    def test_invalid(self):
        lfoods = user_ingredient.load_lfoods(self.USER)
        lfoods_nutrients = food_nutrient.get_foods_nutrients(self.USER, lfoods)
        self.assertIsNone(food_nutrient.get_nutrient_amount_in_foods(lfoods, lfoods_nutrients, INVALID_NUTRIENT_ID))


class TestLogicFoodNutrientGetNutrientAmountInParents(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.USER_FOOD = test_objects.get_user_ingredient()
        test_objects.get_user_ingredient_2()
        test_objects.get_user_food_portion()
        test_objects.get_user_food_nutrient()
        test_objects.get_db_food_nutrient()
        cls.USER_RECIPE = test_objects.get_recipe()
        test_objects.get_user_recipe_portion()
        lfood = user_ingredient.load_lfood(cls.USER, id_=cls.USER_FOOD.id)
        ufm = test_objects.get_user_food_membership(cls.USER_RECIPE, lfood)
        test_objects.get_user_food_membership_portion(ufm)

    def test_nutrient(self):
        lrecipes = user_recipe.load_lrecipes(self.USER)
        lfoods = data_loaders.load_lfoods_for_lparents(self.USER, lrecipes)
        lfoods_nutrients = food_nutrient.get_foods_nutrients(self.USER, lfoods)
        self.assertEqual(
            25, food_nutrient.get_nutrient_amount_in_lparents(lrecipes, lfoods_nutrients, constants.ENERGY_NUTRIENT_ID)
        )

    def test_unavailable_nutrient(self):
        lrecipes = user_recipe.load_lrecipes(self.USER)
        lfoods = data_loaders.load_lfoods_for_lparents(self.USER, lrecipes)
        lfoods_nutrients = food_nutrient.get_foods_nutrients(self.USER, lfoods)
        self.assertIsNone(
            food_nutrient.get_nutrient_amount_in_lparents(lrecipes, lfoods_nutrients, constants.FAT_NUTRIENT_ID)
        )

    def test_invalid(self):
        lrecipes = user_recipe.load_lrecipes(self.USER)
        lfoods = data_loaders.load_lfoods_for_lparents(self.USER, lrecipes)
        lfoods_nutrients = food_nutrient.get_foods_nutrients(self.USER, lfoods)
        self.assertIsNone(
            food_nutrient.get_nutrient_amount_in_lparents(lrecipes, lfoods_nutrients, INVALID_NUTRIENT_ID)
        )


class TestLogicFoodNutrientGetNutrientAmountInMealplan(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.USER_FOOD = test_objects.get_user_ingredient()
        lfood_2 = test_objects.get_user_ingredient_2()
        test_objects.get_user_food_portion()
        test_objects.get_user_food_nutrient()
        test_objects.get_db_food_nutrient()
        cls.USER_RECIPE = test_objects.get_recipe()
        test_objects.get_user_recipe_portion()
        lfood = user_ingredient.load_lfood(cls.USER, id_=cls.USER_FOOD.id)
        ufm = test_objects.get_user_food_membership(cls.USER_RECIPE, lfood)
        test_objects.get_user_food_membership_portion(ufm)
        cls.QUANTITY_MAP = {
            lfood.external_id: 5,
            lfood_2.external_id: 15,
            cls.USER_RECIPE.external_id: 8,
        }

    def test_nutrient(self):
        lrecipes = user_recipe.load_lrecipes(self.USER)
        lfoods = user_ingredient.load_lfoods(self.USER)
        lfoods_nutrients = food_nutrient.get_foods_nutrients(self.USER, lfoods)
        self.assertEqual(
            7,
            food_nutrient.get_nutrient_amount_in_mealplan(
                lfoods, lrecipes, self.QUANTITY_MAP, lfoods_nutrients, constants.ENERGY_NUTRIENT_ID
            ),
        )

    def test_invalid(self):
        lrecipes = user_recipe.load_lrecipes(self.USER)
        lfoods = user_ingredient.load_lfoods(self.USER)
        lfoods_nutrients = food_nutrient.get_foods_nutrients(self.USER, lfoods)
        self.assertIsNone(
            food_nutrient.get_nutrient_amount_in_mealplan(
                lfoods, lrecipes, self.QUANTITY_MAP, lfoods_nutrients, INVALID_NUTRIENT_ID
            )
        )


class TestLogicFoodNutrientGetRecentFoodsForNutrient(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        lfood = test_objects.get_user_ingredient()
        lmeal = test_objects.get_meal_today_1()
        test_objects.get_user_food_nutrient()
        test_objects.get_user_food_membership(lmeal, lfood)

    def test_recent_foods(self):
        recent_foods = food_nutrient.get_recent_foods_for_nutrient(self.USER, constants.ENERGY_NUTRIENT_ID)
        self.assertTrue(recent_foods)


def load_cfoods(**kwargs):
    return [test_objects.get_db_food()]


class TestLogicFoodNutrientGetTopCFoodsForNutrient(TestCase):
    @patch(target="nutrition_tracker.models.db_food.load_cfoods", wraps=load_cfoods)
    def test_recent_cfoods(self, mock_load_cfoods):
        recent_cfoods = food_nutrient.get_top_cfoods_for_nutrient(constants.ENERGY_NUTRIENT_ID)
        self.assertTrue(recent_cfoods)


class TestLogicFoodNutrientGetTrackerNutrients(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        lfood = test_objects.get_user_ingredient()
        lmeal = test_objects.get_meal_today_1()
        test_objects.get_user_food_nutrient()
        ufm = test_objects.get_user_food_membership(lmeal, lfood)
        test_objects.get_user_food_membership_portion(ufm)

    def test_valid_response(self):
        response = food_nutrient.get_tracker_nutrients(self.USER, constants.ENERGY_NUTRIENT_ID)
        self.assertTrue(response)
