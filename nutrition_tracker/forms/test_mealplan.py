from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.constants import constants
from nutrition_tracker.forms import MealplanFormOne, MealplanFormThree, MealplanFormTwo
from nutrition_tracker.logic import mealplan
from nutrition_tracker.tests import constants as test_constants
from nutrition_tracker.tests import objects as test_objects
from nutrition_tracker.utils import form as form_utils


class TestFormsMealplanForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.USER_INGREDIENT = test_objects.get_user_ingredient()
        test_objects.get_user_food_nutrient()
        test_objects.get_user_food_portion()
        cls.USER_INGREDIENT_2 = test_objects.get_user_ingredient_2()
        test_objects.get_user_2_food_nutrient()
        test_objects.get_user_2_food_portion()
        test_objects.get_nutrient_preference()

    def test_form_one_empty_init(self):
        kwargs = {"user": self.USER}
        form = MealplanFormOne(data={}, **kwargs)
        self.assertTrue(form.is_valid())

    def test_form_one_init(self):
        kwargs = {"user": self.USER}
        form_data = {
            "available_foods": [test_constants.TEST_UUID, test_constants.TEST_UUID_2],
            "must_have_foods": [test_constants.TEST_UUID],
            "dont_have_recipes": [test_constants.TEST_UUID_2],
            "dont_repeat_foods": [test_constants.TEST_UUID],
            "dont_repeat_recipes": [
                test_constants.TEST_UUID,
                test_constants.TEST_UUID_2,
                test_constants.TEST_UUID_3,
                test_constants.TEST_UUID_4,
            ],
        }
        form = MealplanFormOne(data=form_data, **kwargs)
        self.assertTrue(form.is_valid())

    def test_form_one_init_invalid(self):
        kwargs = {"user": self.USER}
        form_data = {"available_foods": ["notauuid"]}
        form = MealplanFormOne(data=form_data, **kwargs)
        self.assertFalse(form.is_valid())

    def test_form_two_empty_init(self):
        kwargs = {"user": self.USER}
        form = MealplanFormTwo(data={}, **kwargs)
        self.assertTrue(form.is_valid())

    def test_form_two_init(self):
        kwargs = {"user": self.USER}
        form_data = {
            form_utils.get_field_name(test_constants.TEST_UUID): 29,
            form_utils.get_threshold_field_name(test_constants.TEST_UUID): constants.Threshold.MAX_VALUE,
            form_utils.get_field_name(test_constants.TEST_UUID_2): 32,
            form_utils.get_threshold_field_name(test_constants.TEST_UUID_2): constants.Threshold.EXACT_VALUE,
        }
        form = MealplanFormTwo(data=form_data, **kwargs)
        self.assertTrue(form.is_valid())

    def test_form_three_empty_init(self):
        kwargs = {"user": self.USER}
        form = MealplanFormThree(data={}, **kwargs)
        self.assertTrue(form.is_valid())

    def test_form_three_init(self):
        kwargs = {"user": self.USER}
        form_data = {
            form_utils.get_field_name(test_constants.TEST_UUID): 29,
            form_utils.get_meal_field_name(test_constants.TEST_UUID): constants.MealType.BREAKFAST,
            form_utils.get_field_name(test_constants.TEST_UUID_2): 32,
            form_utils.get_meal_field_name(test_constants.TEST_UUID_2): constants.MealType.LUNCH,
        }
        form = MealplanFormThree(data=form_data, **kwargs)
        self.assertTrue(form.is_valid())

    def test_form_three_init_with_mealplan(self):
        lmealplan = mealplan.get_mealplan_for_user(self.USER)
        kwargs = {"user": self.USER, "lmealplan": lmealplan}
        form_data = {
            form_utils.get_field_name(test_constants.TEST_UUID): 29,
            form_utils.get_meal_field_name(test_constants.TEST_UUID): constants.MealType.BREAKFAST,
            form_utils.get_field_name(test_constants.TEST_UUID_2): 32,
            form_utils.get_meal_field_name(test_constants.TEST_UUID_2): constants.MealType.LUNCH,
        }
        form = MealplanFormThree(data=form_data, **kwargs)
        self.assertTrue(form.is_valid())
