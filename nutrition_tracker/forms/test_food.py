from __future__ import annotations

from crispy_forms.utils import render_crispy_form
from django.test import TransactionTestCase

from nutrition_tracker.biz import user
from nutrition_tracker.constants import constants
from nutrition_tracker.forms import FoodForm, FoodPortionFormset, FoodPortionFormsetHelper
from nutrition_tracker.logic import food_nutrient, food_portion
from nutrition_tracker.models import user_branded_food, user_food_nutrient, user_food_portion, user_ingredient
from nutrition_tracker.tests import objects as test_objects
from nutrition_tracker.tests import utils as test_utils
from nutrition_tracker.utils import form as form_utils


class TestFormsFoodForm(TransactionTestCase):
    reset_sequences = True
    maxDiff = None

    def setUp(self):
        self.USER = test_objects.get_user()
        self.USER_FOOD = test_objects.get_user_ingredient()

    def test_form_empty_init(self):
        kwargs = {"user": self.USER}
        form = FoodForm(**kwargs)
        servings = FoodPortionFormset()

        context = {"servings": servings, "servings_helper": FoodPortionFormsetHelper(servings)}
        with open("%s/test_form_food_empty_init.txt" % test_utils.get_golden_dir()) as golden:
            self.assertHTMLEqual(golden.read(), render_crispy_form(form, context=context))

    def test_form_lfood_blank_init(self):
        lfood = user_ingredient.load_lfood(self.USER, id_=self.USER_FOOD.id)
        kwargs = {"user": self.USER, "lfood": lfood}
        form = FoodForm(**kwargs)
        servings = FoodPortionFormset()

        context = {"servings": servings, "servings_helper": FoodPortionFormsetHelper(servings)}
        with open("%s/test_form_lfood_blank_init.txt" % test_utils.get_golden_dir()) as golden:
            expected_output = golden.read().replace("{FOOD_EXTERNAL_ID}", str(lfood.external_id))
            self.assertHTMLEqual(expected_output, render_crispy_form(form, context=context))

    def test_form_lfood_with_defaults_init(self):
        test_objects.get_user_food_portion()
        test_objects.get_user_food_nutrient()

        # Load objects with data
        lfood = user_ingredient.load_lfood(self.USER, id_=self.USER_FOOD.id)
        food_nutrients = food_nutrient.get_food_nutrients(lfood, lfood.db_food)
        food_portions = food_portion.for_display_choices(lfood, cfood=lfood.db_food)
        kwargs = {"user": self.USER, "lfood": lfood, "food_portions": food_portions, "food_nutrients": food_nutrients}
        form = FoodForm(**kwargs)
        servings = FoodPortionFormset(instance=lfood)

        context = {"servings": servings, "servings_helper": FoodPortionFormsetHelper(servings)}
        with open("%s/test_form_lfood_with_defaults_init.txt" % test_utils.get_golden_dir()) as golden:
            expected_output = golden.read().replace("{FOOD_EXTERNAL_ID}", str(lfood.external_id))
            self.assertHTMLEqual(expected_output, render_crispy_form(form, context=context))

    def test_form_lfood_save(self):
        lfood_portion = test_objects.get_user_food_portion()
        test_objects.get_user_food_nutrient()
        lfood = user_ingredient.load_lfood(self.USER, id_=self.USER_FOOD.id)

        # Load objects with data
        lfood = user_ingredient.load_lfood(self.USER, id_=self.USER_FOOD.id)
        food_nutrients = food_nutrient.get_food_nutrients(lfood, lfood.db_food)
        food_portions = food_portion.for_display_choices(lfood, cfood=lfood.db_food)
        kwargs = {"user": self.USER, "lfood": lfood, "food_portions": food_portions, "food_nutrients": food_nutrients}
        form_data = {
            # Metadata fields
            "name": "My Food",
            "category_id": "2",
            "brand_name": "My Brand Name",
            "brand_owner": "My Brand Owner",
            # Servings management form data
            "nutrition_tracker-userfoodportion-content_type-object_id-TOTAL_FORMS": "2",
            "nutrition_tracker-userfoodportion-content_type-object_id-INITIAL_FORMS": "1",
            "nutrition_tracker-userfoodportion-content_type-object_id-MIN_NUM_FORMS": "0",
            "nutrition_tracker-userfoodportion-content_type-object_id-MAX_NUM_FORMS": "1000",
            # First serving (existing)
            "nutrition_tracker-userfoodportion-content_type-object_id-0-id": lfood_portion.id,
            "nutrition_tracker-userfoodportion-content_type-object_id-0-serving_size": 100,
            "nutrition_tracker-userfoodportion-content_type-object_id-0-serving_size_unit": constants.ServingSizeUnit.WEIGHT,
            # Second serving (new)
            "nutrition_tracker-userfoodportion-content_type-object_id-1-servings_per_container": 2,
            "nutrition_tracker-userfoodportion-content_type-object_id-1-serving_size": 53,
            "nutrition_tracker-userfoodportion-content_type-object_id-1-serving_size_unit": constants.ServingSizeUnit.WEIGHT,
            "nutrition_tracker-userfoodportion-content_type-object_id-1-household_quantity": "1/8",
            "nutrition_tracker-userfoodportion-content_type-object_id-1-measure_unit": 1000,
            # Nutrients (existing)
            form_utils.get_field_name(constants.ENERGY_NUTRIENT_ID): 53,
            # Nutrients (new)
            form_utils.get_field_name(constants.FAT_NUTRIENT_ID): 23,
            form_utils.get_field_name(constants.PROTEIN_NUTRIENT_ID): 89,
        }
        form = FoodForm(data=form_data, **kwargs)
        servings = FoodPortionFormset(form_data, instance=lfood)

        self.assertTrue(form.is_valid())
        self.assertTrue(servings.is_valid())
        form.save(servings)

        lfood.refresh_from_db()
        self.assertEqual("My Food", lfood.name)
        self.assertEqual(2, lfood.category_id)
        self.assertEqual(1, user_branded_food.load_lbranded_foods(self.USER).count())
        self.assertEqual(2, user_food_portion.load_lfood_portions(self.USER).count())
        self.assertEqual(3, user_food_nutrient.load_nutrients(self.USER).count())

    def test_form_lfood_family_save(self):
        lfood = user_ingredient.load_lfood(self.USER, id_=self.USER_FOOD.id)
        luser_2 = test_objects.get_user_2()
        user.create_family(self.USER, luser_2.email)
        self.USER.refresh_from_db()
        luser_2.refresh_from_db()

        kwargs = {"user": luser_2, "lfood": lfood}
        form_data = {
            # Metadata fields
            "name": "My Food",
            "brand_name": "My Brand Name",
            "brand_owner": "My Brand Owner",
            # Servings management form data
            "nutrition_tracker-userfoodportion-content_type-object_id-TOTAL_FORMS": "1",
            "nutrition_tracker-userfoodportion-content_type-object_id-INITIAL_FORMS": "0",
            "nutrition_tracker-userfoodportion-content_type-object_id-MIN_NUM_FORMS": "0",
            "nutrition_tracker-userfoodportion-content_type-object_id-MAX_NUM_FORMS": "1000",
            # First serving (new)
            "nutrition_tracker-userfoodportion-content_type-object_id-0-servings_per_container": 2,
            "nutrition_tracker-userfoodportion-content_type-object_id-0-serving_size": 53,
            "nutrition_tracker-userfoodportion-content_type-object_id-0-serving_size_unit": constants.ServingSizeUnit.WEIGHT,
            "nutrition_tracker-userfoodportion-content_type-object_id-0-household_quantity": "1/8",
            "nutrition_tracker-userfoodportion-content_type-object_id-0-measure_unit": 1000,
            # Nutrients (new)
            form_utils.get_field_name(constants.ENERGY_NUTRIENT_ID): 53,
            form_utils.get_field_name(constants.FAT_NUTRIENT_ID): 23,
            form_utils.get_field_name(constants.PROTEIN_NUTRIENT_ID): 89,
        }
        form = FoodForm(data=form_data, **kwargs)
        servings = FoodPortionFormset(form_data, instance=lfood)

        self.assertTrue(form.is_valid())
        self.assertTrue(servings.is_valid())
        form.save(servings)

        lfood.refresh_from_db()
        self.assertEqual("My Food", lfood.name)
        self.assertEqual(1, user_branded_food.load_lbranded_foods(self.USER).count())
        self.assertEqual(1, user_food_portion.load_lfood_portions(self.USER).count())
        self.assertEqual(3, user_food_nutrient.load_nutrients(self.USER).count())
        self.assertEqual(1, user_branded_food.load_lbranded_foods(luser_2).count())
        self.assertEqual(1, user_food_portion.load_lfood_portions(luser_2).count())
        self.assertEqual(3, user_food_nutrient.load_nutrients(luser_2).count())
