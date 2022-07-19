from __future__ import annotations

from django.test import SimpleTestCase, TestCase, TransactionTestCase

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import data_loaders, food_portion
from nutrition_tracker.models import (
    db_food,
    db_food_portion,
    user_food_portion,
    user_ingredient,
    user_meal,
    user_recipe,
)
from nutrition_tracker.tests import objects as test_objects


class TestLogicFoodPortionGetDefaultPortionChoice(SimpleTestCase):
    def test_weight_choices(self):
        expected_output = [(-1, 100, 100, "g", "g"), (-2, 1, 1, "g", "g"), (-3, 28.3495, 1, "oz", "oz")]
        self.assertEqual(
            expected_output,
            food_portion.get_default_portion_choices(serving_size_unit=constants.ServingSizeUnit.WEIGHT),
        )

    def test_volume_choices(self):
        expected_output = [(-1, 100, 100, "ml", "ml"), (-2, 1, 1, "ml", "ml"), (-3, 29.5735, 1, "fl oz", "us_oz")]
        self.assertEqual(
            expected_output,
            food_portion.get_default_portion_choices(serving_size_unit=constants.ServingSizeUnit.VOLUME),
        )


class TestLogicFoodPortionGetMeasureUnitById(SimpleTestCase):
    def test_success(self):
        return_value = food_portion.get_measure_unit_by_id(1000)
        self.assertEqual("cup", return_value.name)

    def test_missing(self):
        return_value = food_portion.get_measure_unit_by_id(102312321)
        self.assertIsNone(return_value)


class TestLogicFoodPortionGetMeasureUnitByName(SimpleTestCase):
    def test_success(self):
        return_value = food_portion.get_measure_unit_by_name("cup")
        self.assertEqual(1000, return_value.id_)

    def test_missing(self):
        return_value = food_portion.get_measure_unit_by_name("unknown")
        self.assertIsNone(return_value)


class TestLogicFoodPortionForDisplayPortion(SimpleTestCase):
    def test_one(self):
        portion = user_food_portion.UserFoodPortion(
            serving_size=54, serving_size_unit=constants.ServingSizeUnit.VOLUME
        )
        self.assertEqual("54ml", food_portion.for_display_portion(portion))

    def test_two(self):
        portion = user_food_portion.UserFoodPortion(
            servings_per_container=5,
            serving_size=54,
            serving_size_unit=constants.ServingSizeUnit.VOLUME,
            quantity=3,
            amount=2,
            measure_unit_id=1000,
            portion_description="PD",
            modifier="modifier",
        )
        self.assertEqual("6 cup (54ml)", food_portion.for_display_portion(portion))

    def test_three(self):
        portion = db_food_portion.DBFoodPortion(
            amount=2,
            measure_unit_id=1000,
            portion_description="PD",
            modifier="modifier",
            serving_size=34,
            serving_size_unit=constants.ServingSizeUnit.WEIGHT,
        )
        self.assertEqual("2 cup (34g)", food_portion.for_display_portion(portion))

    def test_four(self):
        portion = user_food_portion.UserFoodPortion(
            serving_size=54,
            serving_size_unit=constants.ServingSizeUnit.VOLUME,
            quantity=3,
            amount=2,
            measure_unit_id=constants.UNDETERMINED_MEASURE_UNIT_ID,
            portion_description="PD",
            modifier="modifier",
        )
        self.assertEqual("6 modifier (54ml)", food_portion.for_display_portion(portion))

    def test_five(self):
        portion = user_food_portion.UserFoodPortion(
            serving_size=54,
            serving_size_unit=constants.ServingSizeUnit.VOLUME,
            quantity=3,
            measure_unit_id=constants.UNDETERMINED_MEASURE_UNIT_ID,
            portion_description="PD",
            modifier="modifier",
        )
        self.assertEqual("3 (PD) (54ml)", food_portion.for_display_portion(portion))


class TestLogicFoodPortionForDisplayChoices(TransactionTestCase):
    reset_sequences = True
    maxDiff = None

    def setUp(self):
        self.USER = test_objects.get_user()

    def test_default_choices(self):
        lfood = test_objects.get_user_ingredient()
        expected_output = [
            (-1, "100g", 100, "g", None, None),
            (-2, "1g", 1, "g", None, None),
            (-3, "1oz", 28.3495, "g", None, None),
        ]
        self.assertEqual(expected_output, food_portion.for_display_choices(lfood))

    def test_lfood_no_cfood_with_user_portions(self):
        lfood = test_objects.get_user_ingredient()
        lfood_portion = test_objects.get_user_food_portion()
        lfood = user_ingredient.load_lfood(self.USER, id_=lfood.id)
        expected_output = [
            (lfood_portion.external_id, "83g", 83.0, "g", None, None),
            (-1, "100g", 100, "g", None, None),
            (-2, "1g", 1, "g", None, None),
            (-3, "1oz", 28.3495, "g", None, None),
        ]
        self.assertEqual(expected_output, food_portion.for_display_choices(lfood, cfood=lfood.db_food))

    def test_lfood_with_cfood_defaults(self):
        lfood = test_objects.get_user_ingredient()
        expected_output = [
            (-1, "100g", 100, "g", None, None),
            (-2, "1g", 1, "g", None, None),
            (-3, "1oz", 28.3495, "g", None, None),
        ]
        self.assertEqual(expected_output, food_portion.for_display_choices(lfood))

    def test_lfood_with_cfood_with_user_and_db_portions(self):
        lfood = test_objects.get_user_ingredient()
        lfood_portion = test_objects.get_user_food_portion()
        cfood_portion = test_objects.get_db_food_portion()
        lfood = user_ingredient.load_lfood(self.USER, id_=lfood.id)
        cfood = db_food.load_cfood(id_=lfood.db_food.id)
        expected_output = [
            (lfood_portion.external_id, "83g", 83.0, "g", None, None),
            (cfood_portion.external_id, "100g", 100.0, "g", None, None),
            (-1, "100g", 100, "g", None, None),
            (-2, "1g", 1, "g", None, None),
            (-3, "1oz", 28.3495, "g", None, None),
        ]
        self.assertEqual(expected_output, food_portion.for_display_choices(lfood, cfood=cfood))

    def test_lfood_with_branded_cfood_with_user_and_db_portions(self):
        lfood = test_objects.get_user_ingredient()
        lfood_portion = test_objects.get_user_food_portion()
        cfood_portion = test_objects.get_db_food_branded_portion()
        lfood = user_ingredient.load_lfood(self.USER, id_=lfood.id)
        cfood = db_food.load_cfood(id_=lfood.db_food.id)
        expected_output = [
            (lfood_portion.external_id, "83g", 83.0, "g", None, None),
            (cfood_portion.external_id, "4 cups (50g)", 50.0, "g", None, None),
            (-1, "100g", 100, "g", None, None),
            (-2, "1g", 1, "g", None, None),
            (-3, "1oz", 28.3495, "g", None, None),
        ]
        self.assertEqual(expected_output, food_portion.for_display_choices(lfood, cfood=cfood))

    def test_lrecipe_with_user_portions(self):
        lrecipe = test_objects.get_recipe()
        lfood_portion = test_objects.get_user_recipe_portion()
        lrecipe = user_recipe.load_lrecipe(self.USER, id_=lrecipe.id)
        expected_output = [
            (lfood_portion.external_id, "200g", 200.0, "g", None, None),
            (-1, "100g", 100, "g", None, None),
            (-2, "1g", 1, "g", None, None),
            (-3, "1oz", 28.3495, "g", None, None),
        ]
        self.assertEqual(expected_output, food_portion.for_display_choices(lrecipe))


class TestLogicFoodPortionGetFoodMemberPortion(TransactionTestCase):
    reset_sequences = True
    maxDiff = None

    def setUp(self):
        self.USER = test_objects.get_user()

    def test_get_food_member_portion(self):
        lfood = test_objects.get_user_ingredient()
        cfood = test_objects.get_db_food()
        test_objects.get_user_food_portion()
        lmeal = test_objects.get_meal_today_1()
        ufm = test_objects.get_user_food_membership(lmeal, lfood)
        ufmp = test_objects.get_user_food_membership_portion(ufm)
        food_portions = food_portion.for_display_choices(lfood, cfood=cfood)
        expected_output = ((-2, "1g", 1, "g", None, None), 50)
        self.assertEqual(expected_output, food_portion.get_food_member_portion(ufmp, food_portions))


class TestLogicFoodPortionGetServingSizeInMeals(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.USER_MEAL = test_objects.get_meal_today_1()
        cls.USER_FOOD = test_objects.get_user_ingredient()
        ufm = test_objects.get_user_food_membership(cls.USER_MEAL, cls.USER_FOOD)
        test_objects.get_user_food_membership_portion(ufm)

    def test_food_serving_size(self):
        test_objects.get_meal_today_2()
        lmeals = user_meal.load_lmeals(self.USER)
        self.assertEqual(
            50,
            food_portion.get_serving_size_in_meals(
                lmeals, self.USER_FOOD, data_loaders.get_content_type_ingredient_id()
            ),
        )

    def test_recipe_serving_size(self):
        test_objects.get_meal_today_2()
        lrecipe = test_objects.get_recipe()
        ufm = test_objects.get_user_food_membership(self.USER_MEAL, lrecipe)
        test_objects.get_user_food_membership_portion(ufm)

        lmeals = user_meal.load_lmeals(self.USER)
        self.assertEqual(
            50, food_portion.get_serving_size_in_meals(lmeals, lrecipe, data_loaders.get_content_type_recipe_id())
        )

    def test_serving_size_no_member(self):
        test_objects.get_meal_today_2()
        lrecipe = test_objects.get_recipe()
        lmeals = user_meal.load_lmeals(self.USER)
        self.assertEqual(
            0, food_portion.get_serving_size_in_meals(lmeals, lrecipe, data_loaders.get_content_type_recipe_id())
        )


class TestLogicFoodPortionGetCategoryServingSizeInMeals(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.USER_MEAL = test_objects.get_meal_today_1()
        cls.USER_FOOD = test_objects.get_user_ingredient()
        ufm = test_objects.get_user_food_membership(cls.USER_MEAL, cls.USER_FOOD)
        test_objects.get_user_food_membership_portion(ufm)

    def test_food_present(self):
        test_objects.get_meal_today_2()
        lmeals = user_meal.load_lmeals(self.USER)
        self.assertEqual(50, food_portion.get_category_serving_size_in_meals(lmeals, [self.USER_FOOD]))

    def test_food_not_present(self):
        test_objects.get_meal_today_2()
        lfood = test_objects.get_user_ingredient_2()
        lmeals = user_meal.load_lmeals(self.USER)
        self.assertEqual(0, food_portion.get_category_serving_size_in_meals(lmeals, [lfood]))


class TestLogicFoodPortionGetCategoryFoodCountInMeals(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.USER_MEAL = test_objects.get_meal_today_1()
        cls.USER_FOOD = test_objects.get_user_ingredient()
        ufm = test_objects.get_user_food_membership(cls.USER_MEAL, cls.USER_FOOD)
        test_objects.get_user_food_membership_portion(ufm)

    def test_food_present(self):
        test_objects.get_meal_today_2()
        lmeals = user_meal.load_lmeals(self.USER)
        self.assertEqual(1, food_portion.get_category_food_count_in_meals(lmeals, [self.USER_FOOD]))

    def test_food_not_present(self):
        test_objects.get_meal_today_2()
        lfood = test_objects.get_user_ingredient_2()
        lmeals = user_meal.load_lmeals(self.USER)
        self.assertEqual(0, food_portion.get_category_food_count_in_meals(lmeals, [lfood]))

    def test_foods_partial_presence(self):
        test_objects.get_meal_today_2()
        lfood = test_objects.get_user_ingredient_2()
        lmeals = user_meal.load_lmeals(self.USER)
        self.assertEqual(1, food_portion.get_category_food_count_in_meals(lmeals, [self.USER_FOOD, lfood]))
