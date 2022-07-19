from __future__ import annotations

from http import HTTPStatus

from django.contrib.messages import get_messages
from django.test import TestCase, override_settings
from django.urls import reverse

from nutrition_tracker.constants import constants
from nutrition_tracker.models import (
    db_branded_food,
    db_food,
    db_food_nutrient,
    db_food_portion,
    search_result,
    user_branded_food,
    user_food_nutrient,
    user_food_portion,
    user_ingredient,
)
from nutrition_tracker.tests import objects as test_objects
from nutrition_tracker.utils import form as form_utils


class TestViewsMyFoodCreate(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()

    def test_logged_out_redirects(self):
        response = self.client.get(reverse("my_food_create"), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/accounts/login/?next=/my_food_create/")

    def test_logged_in_success(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("my_food_create"), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "nutrition_tracker/my_food_create.html")
        self.assertIsNone(response.context["lfood"])
        self.assertIsNone(response.context["cfood"])
        self.assertIsNone(response.context["lrecipe"])
        self.assertIsNone(response.context["lmeal"])
        self.assertFalse(response.context["lfoods"])
        self.assertFalse(response.context["member_recipes"])
        self.assertFalse(response.context["lmeals"])
        self.assertFalse(response.context["food_nutrients"])
        self.assertFalse(response.context["food_portions"])
        self.assertFalse(response.context["nutrient_preferences"])

    def test_logged_in_save_required_fields_success(self):
        self.client.login(email="user@famnom.com", password="password")
        self.assertEqual(0, user_ingredient.load_lfoods(self.USER).count())

        response = self.client.post(
            reverse("my_food_create"),
            {
                # Metadata fields
                "name": "My Food",
                "brand_name": "My Brand Name",
                "brand_owner": "My Brand Owner",
                # Servings management form data
                "nutrition_tracker-userfoodportion-content_type-object_id-TOTAL_FORMS": "1",
                "nutrition_tracker-userfoodportion-content_type-object_id-INITIAL_FORMS": "0",
                "nutrition_tracker-userfoodportion-content_type-object_id-MIN_NUM_FORMS": "0",
                "nutrition_tracker-userfoodportion-content_type-object_id-MAX_NUM_FORMS": "1000",
                # Empty first portion
                "nutrition_tracker-userfoodportion-content_type-object_id-0-serving_size": "",
                "nutrition_tracker-userfoodportion-content_type-object_id-0-serving_size_unit": "",
                # Required nutrient data
                form_utils.get_field_name(constants.ENERGY_NUTRIENT_ID): 53,
            },
            follow=True,
        )
        self.assertEqual(1, user_ingredient.load_lfoods(self.USER).count())
        self.assertEqual(1, db_food.load_cfoods().count())
        self.assertEqual(0, user_branded_food.load_lbranded_foods(self.USER).count())
        self.assertEqual(1, db_branded_food.load_cbranded_foods().count())
        self.assertEqual(0, user_food_portion.load_lfood_portions(self.USER).count())
        self.assertEqual(0, db_food_portion.load_portions().count())
        self.assertEqual(0, user_food_nutrient.load_nutrients(self.USER).count())
        self.assertEqual(1, db_food_nutrient.load_nutrients().count())
        self.assertEqual(1, search_result.load_results().count())
        lfood = user_ingredient.load_lfoods(self.USER).first()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/my_ingredient/%s/" % lfood.external_id)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_SUCCESS_FOOD_SAVE, messages)

    def test_logged_in_save_all_fields_index_success(self):
        self.client.login(email="user@famnom.com", password="password")
        self.assertEqual(0, user_ingredient.load_lfoods(self.USER).count())

        response = self.client.post(
            reverse("my_food_create"),
            {
                # Metadata fields
                "name": "My Food",
                "brand_name": "My Brand Name",
                "brand_owner": "My Brand Owner",
                # Servings management form data
                "nutrition_tracker-userfoodportion-content_type-object_id-TOTAL_FORMS": "2",
                "nutrition_tracker-userfoodportion-content_type-object_id-INITIAL_FORMS": "0",
                "nutrition_tracker-userfoodportion-content_type-object_id-MIN_NUM_FORMS": "0",
                "nutrition_tracker-userfoodportion-content_type-object_id-MAX_NUM_FORMS": "1000",
                # First portion
                "nutrition_tracker-userfoodportion-content_type-object_id-0-servings_per_container": 3,
                "nutrition_tracker-userfoodportion-content_type-object_id-0-serving_size": 77,
                "nutrition_tracker-userfoodportion-content_type-object_id-0-serving_size_unit": constants.ServingSizeUnit.VOLUME,
                "nutrition_tracker-userfoodportion-content_type-object_id-0-household_quantity": "1/8",
                "nutrition_tracker-userfoodportion-content_type-object_id-0-measure_unit": 1000,
                # Second portion
                "nutrition_tracker-userfoodportion-content_type-object_id-1-servings_per_container": "",
                "nutrition_tracker-userfoodportion-content_type-object_id-1-serving_size": 10,
                "nutrition_tracker-userfoodportion-content_type-object_id-1-serving_size_unit": constants.ServingSizeUnit.VOLUME,
                # Required nutrient data
                form_utils.get_field_name(constants.ENERGY_NUTRIENT_ID): 53,
                form_utils.get_field_name(constants.FAT_NUTRIENT_ID): 23,
                form_utils.get_field_name(constants.PROTEIN_NUTRIENT_ID): 89,
            },
            follow=True,
        )
        self.assertEqual(1, user_ingredient.load_lfoods(self.USER).count())
        self.assertEqual(1, db_food.load_cfoods().count())
        self.assertEqual(0, user_branded_food.load_lbranded_foods(self.USER).count())
        self.assertEqual(1, db_branded_food.load_cbranded_foods().count())
        self.assertEqual(0, user_food_portion.load_lfood_portions(self.USER).count())
        self.assertEqual(2, db_food_portion.load_portions().count())
        self.assertEqual(0, user_food_nutrient.load_nutrients(self.USER).count())
        self.assertEqual(3, db_food_nutrient.load_nutrients().count())
        self.assertEqual(1, search_result.load_results().count())
        lfood = user_ingredient.load_lfoods(self.USER).first()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/my_ingredient/%s/" % lfood.external_id)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_SUCCESS_FOOD_SAVE, messages)

    def test_logged_in_save_all_fields_do_not_index_success(self):
        self.client.login(email="user@famnom.com", password="password")
        self.assertEqual(0, user_ingredient.load_lfoods(self.USER).count())

        response = self.client.post(
            reverse("my_food_create"),
            {
                # Metadata fields
                "name": "My Food",
                "brand_name": "My Brand Name",
                "brand_owner": "My Brand Owner",
                # Servings management form data
                "nutrition_tracker-userfoodportion-content_type-object_id-TOTAL_FORMS": "2",
                "nutrition_tracker-userfoodportion-content_type-object_id-INITIAL_FORMS": "0",
                "nutrition_tracker-userfoodportion-content_type-object_id-MIN_NUM_FORMS": "0",
                "nutrition_tracker-userfoodportion-content_type-object_id-MAX_NUM_FORMS": "1000",
                # First portion
                "nutrition_tracker-userfoodportion-content_type-object_id-0-servings_per_container": 3,
                "nutrition_tracker-userfoodportion-content_type-object_id-0-serving_size": 77,
                "nutrition_tracker-userfoodportion-content_type-object_id-0-serving_size_unit": constants.ServingSizeUnit.VOLUME,
                "nutrition_tracker-userfoodportion-content_type-object_id-0-household_quantity": "1/8",
                "nutrition_tracker-userfoodportion-content_type-object_id-0-measure_unit": 1000,
                # Second portion
                "nutrition_tracker-userfoodportion-content_type-object_id-1-servings_per_container": "",
                "nutrition_tracker-userfoodportion-content_type-object_id-1-serving_size": 10,
                "nutrition_tracker-userfoodportion-content_type-object_id-1-serving_size_unit": constants.ServingSizeUnit.VOLUME,
                # Required nutrient data
                form_utils.get_field_name(constants.ENERGY_NUTRIENT_ID): 53,
                form_utils.get_field_name(constants.FAT_NUTRIENT_ID): 23,
                form_utils.get_field_name(constants.PROTEIN_NUTRIENT_ID): 89,
            },
            follow=True,
        )
        self.assertEqual(1, user_ingredient.load_lfoods(self.USER).count())
        self.assertEqual(1, db_food.load_cfoods().count())
        self.assertEqual(0, user_branded_food.load_lbranded_foods(self.USER).count())
        self.assertEqual(1, db_branded_food.load_cbranded_foods().count())
        self.assertEqual(0, user_food_portion.load_lfood_portions(self.USER).count())
        self.assertEqual(2, db_food_portion.load_portions().count())
        self.assertEqual(0, user_food_nutrient.load_nutrients(self.USER).count())
        self.assertEqual(3, db_food_nutrient.load_nutrients().count())
        self.assertEqual(0, search_result.load_results().count())
        lfood = user_ingredient.load_lfoods(self.USER).first()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/my_ingredient/%s/" % lfood.external_id)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_SUCCESS_FOOD_SAVE, messages)
