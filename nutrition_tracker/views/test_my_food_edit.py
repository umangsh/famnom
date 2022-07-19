from __future__ import annotations

from http import HTTPStatus

from django.contrib.messages import get_messages
from django.test import TransactionTestCase, override_settings
from django.urls import reverse

from nutrition_tracker.constants import constants
from nutrition_tracker.models import user_branded_food, user_food_nutrient, user_food_portion, user_ingredient
from nutrition_tracker.tests import constants as test_constants
from nutrition_tracker.tests import objects as test_objects
from nutrition_tracker.tests import utils as test_utils
from nutrition_tracker.utils import form as form_utils


class TestViewsMyFoodEdit(TransactionTestCase):
    reset_sequences = True
    maxDiff = None

    def setUp(self):
        self.USER = test_objects.get_user()

    def test_logged_out_redirects(self):
        response = self.client.get(reverse("my_food_edit", kwargs={"id": test_constants.TEST_UUID}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/accounts/login/?next=/my_food_edit/%s/" % test_constants.TEST_UUID)

    def test_logged_in_not_found(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("my_food_edit", kwargs={"id": test_constants.TEST_UUID}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/my_foods/")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_ERROR_MISSING_FOOD, messages)

    @override_settings(DEBUG=False)
    @test_utils.prevent_request_warnings
    def test_bad_id(self):
        response = self.client.get("/my_food_edit/123")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, "errors/404.html")

    def test_logged_in_success(self):
        lfood = test_objects.get_user_ingredient()
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("my_food_edit", kwargs={"id": lfood.external_id}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "nutrition_tracker/my_food_edit.html")
        self.assertEqual(response.context["lfood"], lfood)
        self.assertEqual(response.context["cfood"], lfood.db_food)
        self.assertIsNone(response.context["lrecipe"])
        self.assertIsNone(response.context["lmeal"])
        self.assertFalse(response.context["lfoods"])
        self.assertFalse(response.context["member_recipes"])
        self.assertFalse(response.context["lmeals"])
        self.assertFalse(response.context["food_nutrients"])
        self.assertTrue(response.context["food_portions"])
        self.assertFalse(response.context["nutrient_preferences"])

    def test_logged_in_save_success(self):
        lfood = test_objects.get_user_ingredient()
        lfood_portion = test_objects.get_user_food_portion()
        test_objects.get_user_food_nutrient()
        self.client.login(email="user@famnom.com", password="password")
        self.assertEqual(1, user_ingredient.load_lfoods(self.USER).count())
        self.assertEqual(0, user_branded_food.load_lbranded_foods(self.USER).count())

        response = self.client.post(
            reverse("my_food_edit", kwargs={"id": lfood.external_id}),
            {
                # Metadata fields
                "external_id": lfood.external_id,
                "name": "My Food",
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
            },
            follow=True,
        )
        self.assertEqual(1, user_ingredient.load_lfoods(self.USER).count())
        self.assertEqual(1, user_branded_food.load_lbranded_foods(self.USER).count())
        self.assertEqual(2, user_food_portion.load_lfood_portions(self.USER).count())
        self.assertEqual(3, user_food_nutrient.load_nutrients(self.USER).count())
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/my_ingredient/%s/" % lfood.external_id)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_SUCCESS_FOOD_SAVE, messages)
