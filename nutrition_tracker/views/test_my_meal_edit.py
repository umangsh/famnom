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


class TestViewsMyMealEdit(TransactionTestCase):
    reset_sequences = True
    maxDiff = None

    def setUp(self):
        self.USER = test_objects.get_user()

    def test_logged_out_redirects(self):
        response = self.client.get(reverse("my_meal_edit", kwargs={"id": test_constants.TEST_UUID}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/accounts/login/?next=/my_meal_edit/%s/" % test_constants.TEST_UUID)

    def test_logged_in_not_found(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("my_meal_edit", kwargs={"id": test_constants.TEST_UUID}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/my_meals/")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_ERROR_MISSING_MEAL, messages)

    @override_settings(DEBUG=False)
    @test_utils.prevent_request_warnings
    def test_bad_id(self):
        response = self.client.get("/my_meal_edit/123")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, "errors/404.html")

    def test_logged_in_success(self):
        lmeal = test_objects.get_meal_today_1()
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("my_meal_edit", kwargs={"id": lmeal.external_id}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "nutrition_tracker/my_meal_edit.html")
        self.assertIsNone(response.context["lfood"])
        self.assertIsNone(response.context["cfood"])
        self.assertIsNone(response.context["lrecipe"])
        self.assertEqual(response.context["lmeal"], lmeal)
        self.assertFalse(response.context["lfoods"])
        self.assertFalse(response.context["member_recipes"])
        self.assertFalse(response.context["lmeals"])
        self.assertFalse(response.context["food_nutrients"])
        self.assertFalse(response.context["food_portions"])
        self.assertFalse(response.context["nutrient_preferences"])

    def test_logged_in_save_success(self):
        self.client.login(email="user@famnom.com", password="password")
        lfood = test_objects.get_user_ingredient()
        lrecipe = test_objects.get_recipe()
        lmeal = test_objects.get_meal_today_1()
        self.assertEqual(constants.MealType.BREAKFAST, lmeal.meal_type)

        response = self.client.post(
            reverse("my_meal_edit", kwargs={"id": lmeal.external_id}),
            {
                # Metadata fields
                "external_id": lmeal.external_id,
                "meal_type": constants.MealType.LUNCH,
                "meal_date": lmeal.meal_date,
                # Foods management form data
                "food-TOTAL_FORMS": "1",
                "food-INITIAL_FORMS": "0",
                "food-MIN_NUM_FORMS": "0",
                "food-MAX_NUM_FORMS": "1000",
                # First food
                "food-0-child_external_id": lfood.external_id,
                "food-0-quantity": 3,
                "food-0-serving": -2,
                # Recipes management form data
                "recipe-TOTAL_FORMS": "1",
                "recipe-INITIAL_FORMS": "0",
                "recipe-MIN_NUM_FORMS": "0",
                "recipe-MAX_NUM_FORMS": "1000",
                # First recipe
                "recipe-0-child_external_id": lrecipe.external_id,
                "recipe-0-quantity": 7,
                "recipe-0-serving": -1,
            },
            follow=True,
        )

        lmeal.refresh_from_db()
        self.assertEqual(constants.MealType.LUNCH, lmeal.meal_type)
        self.assertEqual(2, user_food_portion.load_lfood_portions(self.USER).count())
        self.assertEqual(2, user_food_membership.load_lmemberships(self.USER).count())
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/my_meal/%s/" % lmeal.external_id)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_SUCCESS_MEAL_SAVE, messages)
