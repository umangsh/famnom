from __future__ import annotations

from django.test import TransactionTestCase

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import forms as forms_logic
from nutrition_tracker.logic import user_prefs
from nutrition_tracker.models import db_food, user_ingredient, user_recipe
from nutrition_tracker.tests import objects as test_objects


class TestLogicFormsGetPortionChoicesFormData(TransactionTestCase):
    reset_sequences = True
    maxDiff = None

    def setUp(self):
        self.USER = test_objects.get_user()

    def test_lfood_no_cfood_defaults(self):
        lfood = test_objects.get_user_ingredient()
        expected_output = [
            (-1, {"label": "100g", "data-gm-wt": 100, "data-wt-unit": "g"}),
            (-2, {"label": "1g", "data-gm-wt": 1, "data-wt-unit": "g"}),
            (-3, {"label": "1oz", "data-gm-wt": 28.3495, "data-wt-unit": "g"}),
        ]
        self.assertEqual(expected_output, forms_logic.get_portion_choices_form_data(lfood))

    def test_lfood_no_cfood_with_user_portions(self):
        lfood = test_objects.get_user_ingredient()
        lfood_portion = test_objects.get_user_food_portion()
        lfood = user_ingredient.load_lfood(self.USER, id_=lfood.id)
        expected_output = [
            (lfood_portion.external_id, {"label": "83g", "data-gm-wt": 83, "data-wt-unit": "g"}),
            (-1, {"label": "100g", "data-gm-wt": 100, "data-wt-unit": "g"}),
            (-2, {"label": "1g", "data-gm-wt": 1, "data-wt-unit": "g"}),
            (-3, {"label": "1oz", "data-gm-wt": 28.3495, "data-wt-unit": "g"}),
        ]
        self.assertEqual(expected_output, forms_logic.get_portion_choices_form_data(lfood))

    def test_lfood_with_cfood_defaults(self):
        lfood = test_objects.get_user_ingredient()
        expected_output = [
            (-1, {"label": "100g", "data-gm-wt": 100, "data-wt-unit": "g"}),
            (-2, {"label": "1g", "data-gm-wt": 1, "data-wt-unit": "g"}),
            (-3, {"label": "1oz", "data-gm-wt": 28.3495, "data-wt-unit": "g"}),
        ]
        self.assertEqual(expected_output, forms_logic.get_portion_choices_form_data(lfood, cfood=lfood.db_food))

    def test_lfood_with_cfood_with_user_and_db_portions(self):
        lfood = test_objects.get_user_ingredient()
        lfood_portion = test_objects.get_user_food_portion()
        cfood_portion = test_objects.get_db_food_portion()
        lfood = user_ingredient.load_lfood(self.USER, id_=lfood.id)
        cfood = db_food.load_cfood(id_=lfood.db_food.id)
        expected_output = [
            (lfood_portion.external_id, {"label": "83g", "data-gm-wt": 83.0, "data-wt-unit": "g"}),
            (cfood_portion.external_id, {"label": "100g", "data-gm-wt": 100.0, "data-wt-unit": "g"}),
            (-1, {"label": "100g", "data-gm-wt": 100, "data-wt-unit": "g"}),
            (-2, {"label": "1g", "data-gm-wt": 1, "data-wt-unit": "g"}),
            (-3, {"label": "1oz", "data-gm-wt": 28.3495, "data-wt-unit": "g"}),
        ]
        self.assertEqual(expected_output, forms_logic.get_portion_choices_form_data(lfood, cfood=cfood))

    def test_lfood_with_branded_cfood_with_user_and_db_portions(self):
        lfood = test_objects.get_user_ingredient()
        lfood_portion = test_objects.get_user_food_portion()
        cfood_portion = test_objects.get_db_food_branded_portion()
        lfood = user_ingredient.load_lfood(self.USER, id_=lfood.id)
        cfood = db_food.load_cfood(id_=lfood.db_food.id)
        expected_output = [
            (lfood_portion.external_id, {"label": "83g", "data-gm-wt": 83.0, "data-wt-unit": "g"}),
            (cfood_portion.external_id, {"label": "4 cups (50g)", "data-gm-wt": 50, "data-wt-unit": "g"}),
            (-1, {"label": "100g", "data-gm-wt": 100, "data-wt-unit": "g"}),
            (-2, {"label": "1g", "data-gm-wt": 1, "data-wt-unit": "g"}),
            (-3, {"label": "1oz", "data-gm-wt": 28.3495, "data-wt-unit": "g"}),
        ]
        self.assertEqual(expected_output, forms_logic.get_portion_choices_form_data(lfood, cfood=cfood))

    def test_lrecipe_with_user_portions(self):
        lrecipe = test_objects.get_recipe()
        lfood_portion = test_objects.get_user_recipe_portion()
        lrecipe = user_recipe.load_lrecipe(self.USER, id_=lrecipe.id)
        expected_output = [
            (lfood_portion.external_id, {"label": "200g", "data-gm-wt": 200, "data-wt-unit": "g"}),
            (-1, {"label": "100g", "data-gm-wt": 100, "data-wt-unit": "g"}),
            (-2, {"label": "1g", "data-gm-wt": 1, "data-wt-unit": "g"}),
            (-3, {"label": "1oz", "data-gm-wt": 28.3495, "data-wt-unit": "g"}),
        ]
        self.assertEqual(expected_output, forms_logic.get_portion_choices_form_data(lrecipe))


class TestLogicFormsProcessPortionChoicesFormData(TransactionTestCase):
    reset_sequences = True
    maxDiff = None

    def setUp(self):
        self.USER = test_objects.get_user()
        lfood = test_objects.get_user_ingredient()
        self.LFOOD_PORTION = test_objects.get_user_food_portion()
        self.CFOOD_PORTION = test_objects.get_db_food_branded_portion()
        self.USER_FOOD = user_ingredient.load_lfood(self.USER, id_=lfood.id)
        self.DB_FOOD = db_food.load_cfood(id_=lfood.db_food.id)

    def test_default_portion(self):
        return_value = forms_logic.process_portion_choices_form_data(4, "-3", self.USER_FOOD, cfood=self.DB_FOOD)
        self.assertIsNone(return_value.servings_per_container)
        self.assertEqual(113.398, return_value.serving_size)
        self.assertEqual(constants.ServingSizeUnit.WEIGHT, return_value.serving_size_unit)
        self.assertEqual(4, return_value.quantity)
        self.assertEqual(1, return_value.amount)
        self.assertEqual(1038, return_value.measure_unit_id)
        self.assertIsNone(return_value.modifier)
        self.assertIsNone(return_value.portion_description)

    def test_branded_portion(self):
        return_value = forms_logic.process_portion_choices_form_data(
            3, str(self.CFOOD_PORTION.external_id), self.USER_FOOD, cfood=self.DB_FOOD
        )
        self.assertIsNone(return_value.servings_per_container)
        self.assertEqual(150, return_value.serving_size)
        self.assertEqual(constants.ServingSizeUnit.WEIGHT, return_value.serving_size_unit)
        self.assertEqual(3, return_value.quantity)
        self.assertIsNone(return_value.amount)
        self.assertIsNone(return_value.measure_unit_id)
        self.assertIsNone(return_value.modifier)
        self.assertEqual("4 cups", return_value.portion_description)

    def test_user_portion(self):
        return_value = forms_logic.process_portion_choices_form_data(
            2, str(self.LFOOD_PORTION.external_id), self.USER_FOOD, cfood=self.DB_FOOD
        )
        self.assertIsNone(return_value.servings_per_container)
        self.assertEqual(166, return_value.serving_size)
        self.assertEqual(constants.ServingSizeUnit.WEIGHT, return_value.serving_size_unit)
        self.assertEqual(2, return_value.quantity)
        self.assertIsNone(return_value.amount)
        self.assertIsNone(return_value.measure_unit_id)
        self.assertIsNone(return_value.modifier)
        self.assertIsNone(return_value.portion_description)

    def test_db_portion(self):
        lfood_2 = test_objects.get_user_ingredient_2()
        cfood_2 = test_objects.get_db_food_2()
        cfood_portion_2 = test_objects.get_db_food_portion_2()
        lfood_2 = user_ingredient.load_lfood(self.USER, id_=lfood_2.id)
        cfood_2 = db_food.load_cfood(id_=cfood_2.id)
        return_value = forms_logic.process_portion_choices_form_data(
            7, str(cfood_portion_2.external_id), lfood_2, cfood=cfood_2
        )
        self.assertIsNone(return_value.servings_per_container)
        self.assertEqual(1029, return_value.serving_size)
        self.assertEqual(constants.ServingSizeUnit.WEIGHT, return_value.serving_size_unit)
        self.assertEqual(7, return_value.quantity)
        self.assertIsNone(return_value.amount)
        self.assertIsNone(return_value.measure_unit_id)
        self.assertIsNone(return_value.modifier)
        self.assertIsNone(return_value.portion_description)


class TestLogicFormsGetServingDefaults(TransactionTestCase):
    reset_sequences = True
    maxDiff = None

    def setUp(self):
        self.USER = test_objects.get_user()

    def test_defaults(self):
        lfood = test_objects.get_user_ingredient()
        serving_size, serving_size_unit = forms_logic.get_serving_defaults(lfood)
        self.assertEqual(constants.PORTION_SIZE, serving_size)
        self.assertEqual(constants.ServingSizeUnit.WEIGHT, serving_size_unit)

    def test_first_portion(self):
        lfood = test_objects.get_user_ingredient()
        test_objects.get_user_food_portion()
        lfood = user_ingredient.load_lfood(self.USER, id_=lfood.id)
        serving_size, serving_size_unit = forms_logic.get_serving_defaults(lfood)
        self.assertEqual(83, serving_size)
        self.assertEqual(constants.ServingSizeUnit.WEIGHT, serving_size_unit)

    def test_branded_portion(self):
        lfood = test_objects.get_user_ingredient()
        test_objects.get_db_food_branded_portion()
        lfood = user_ingredient.load_lfood(self.USER, id_=lfood.id)
        serving_size, serving_size_unit = forms_logic.get_serving_defaults(lfood)
        self.assertEqual(50, serving_size)
        self.assertEqual(constants.ServingSizeUnit.WEIGHT, serving_size_unit)


class TestLogicFormsGetItemsFormDataFromPreferences(TransactionTestCase):
    reset_sequences = True
    maxDiff = None

    def setUp(self):
        self.USER = test_objects.get_user()

    def test_success(self):
        test_objects.get_user_preference()
        test_objects.get_user_preference_2()

        lfood_preferences = list(user_prefs.load_food_preferences(self.USER))
        av, mh, dh, dr = forms_logic.get_items_form_data_from_preferences(lfood_preferences)
        self.assertEqual(1, len(av))
        self.assertEqual(1, len(mh))
        self.assertEqual(0, len(dh))
        self.assertEqual(0, len(dr))
