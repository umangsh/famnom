from __future__ import annotations

from http import HTTPStatus

from django.contrib.messages import get_messages
from django.test import TransactionTestCase, override_settings
from django.urls import reverse

from nutrition_tracker.constants import constants
from nutrition_tracker.models import user_food_membership, user_food_portion
from nutrition_tracker.tests import constants as test_constants
from nutrition_tracker.tests import objects as test_objects
from nutrition_tracker.tests import utils as test_utils


class TestViewsMyRecipeEdit(TransactionTestCase):
    reset_sequences = True
    maxDiff = None

    def setUp(self):
        self.USER = test_objects.get_user()

    def test_logged_out_redirects(self):
        response = self.client.get(reverse("my_recipe_edit", kwargs={"id": test_constants.TEST_UUID}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/accounts/login/?next=/my_recipe_edit/%s/" % test_constants.TEST_UUID)

    def test_logged_in_not_found(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("my_recipe_edit", kwargs={"id": test_constants.TEST_UUID}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/my_recipes/")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_ERROR_MISSING_RECIPE, messages)

    @override_settings(DEBUG=False)
    @test_utils.prevent_request_warnings
    def test_bad_id(self):
        response = self.client.get("/my_recipe_edit/123")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, "errors/404.html")

    def test_logged_in_success(self):
        lrecipe = test_objects.get_recipe()
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("my_recipe_edit", kwargs={"id": lrecipe.external_id}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "nutrition_tracker/my_recipe_edit.html")
        self.assertIsNone(response.context["lfood"])
        self.assertIsNone(response.context["cfood"])
        self.assertEqual(response.context["lrecipe"], lrecipe)
        self.assertIsNone(response.context["lmeal"])
        self.assertFalse(response.context["lfoods"])
        self.assertFalse(response.context["member_recipes"])
        self.assertFalse(response.context["lmeals"])
        self.assertFalse(response.context["food_nutrients"])
        self.assertTrue(response.context["food_portions"])
        self.assertFalse(response.context["nutrient_preferences"])

    def test_logged_in_save_success(self):
        lrecipe = test_objects.get_recipe()
        lrecipe_2 = test_objects.get_recipe_2()
        lfood = test_objects.get_user_ingredient()
        lfood_2 = test_objects.get_user_ingredient_2()
        ufm1 = test_objects.get_user_food_membership(lrecipe, lfood)
        test_objects.get_user_food_membership_portion(ufm1)
        ufm2 = test_objects.get_user_food_membership(lrecipe, lrecipe_2)
        test_objects.get_user_food_membership_portion(ufm2)
        lrecipe_portion = test_objects.get_user_recipe_portion()

        self.client.login(email="user@famnom.com", password="password")
        response = self.client.post(
            reverse("my_recipe_edit", kwargs={"id": lrecipe.external_id}),
            {
                # Metadata fields
                "external_id": lrecipe.external_id,
                "name": "Updated Name",
                "recipe_date": lrecipe.recipe_date,
                # Foods management form data
                "food-TOTAL_FORMS": "2",
                "food-INITIAL_FORMS": "1",
                "food-MIN_NUM_FORMS": "0",
                "food-MAX_NUM_FORMS": "1000",
                # First food (existing)
                "food-0-id": lfood.id,
                "food-0-child_external_id": lfood.external_id,
                "food-0-quantity": 50,
                "food-0-serving": -2,
                # Second food (new)
                "food-1-child_external_id": lfood_2.external_id,
                "food-1-quantity": 3,
                "food-1-serving": -3,
                # Recipes management form data
                "recipe-TOTAL_FORMS": "1",
                "recipe-INITIAL_FORMS": "1",
                "recipe-MIN_NUM_FORMS": "0",
                "recipe-MAX_NUM_FORMS": "1000",
                # First recipe (existing)
                "recipe-0-id": lrecipe_2.id,
                "recipe-0-child_external_id": lrecipe_2.external_id,
                "recipe-0-quantity": 50,
                "recipe-0-serving": -2,
                # Servings management form data
                "servings-TOTAL_FORMS": "2",
                "servings-INITIAL_FORMS": "1",
                "servings-MIN_NUM_FORMS": "0",
                "servings-MAX_NUM_FORMS": "1000",
                # First serving (existing)
                "servings-0-id": lrecipe_portion.id,
                "servings-0-serving_size": 200,
                "servings-0-serving_size_unit": constants.ServingSizeUnit.WEIGHT,
                # Servings (new)
                "servings-1-serving_size": 150,
                "servings-1-serving_size_unit": constants.ServingSizeUnit.WEIGHT,
                "servings-1-household_quantity": "1/8",
                "servings-1-measure_unit": 1000,
            },
            follow=True,
        )

        lrecipe.refresh_from_db()
        self.assertEqual("Updated Name", lrecipe.name)
        self.assertEqual(5, user_food_portion.load_lfood_portions(self.USER).count())
        self.assertEqual(3, user_food_membership.load_lmemberships(self.USER).count())
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/my_recipe/%s/" % lrecipe.external_id)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_SUCCESS_RECIPE_SAVE, messages)
