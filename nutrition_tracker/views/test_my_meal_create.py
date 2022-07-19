from __future__ import annotations

from http import HTTPStatus

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from nutrition_tracker.constants import constants
from nutrition_tracker.models import user_food_membership, user_food_portion, user_ingredient, user_meal, user_recipe
from nutrition_tracker.tests import objects as test_objects


class TestViewsMyMealCreate(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()

    def test_logged_out_redirects(self):
        response = self.client.get(reverse("my_meal_create"), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/accounts/login/?next=/my_meal_create/")

    def test_logged_in_success(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("my_meal_create"), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "nutrition_tracker/my_meal_create.html")
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

    def test_logged_in_save_success(self):
        self.client.login(email="user@famnom.com", password="password")
        lfood = test_objects.get_user_ingredient()
        lrecipe = test_objects.get_recipe()
        self.assertEqual(0, user_meal.load_lmeals(self.USER).count())

        response = self.client.post(
            reverse("my_meal_create"),
            {
                # Metadata fields
                "meal_type": constants.MealType.BREAKFAST,
                "meal_date": timezone.localdate(),
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
        self.assertEqual(1, user_ingredient.load_lfoods(self.USER).count())
        self.assertEqual(1, user_recipe.load_lrecipes(self.USER).count())
        self.assertEqual(2, user_food_portion.load_lfood_portions(self.USER).count())
        self.assertEqual(2, user_food_membership.load_lmemberships(self.USER).count())
        self.assertEqual(1, user_meal.load_lmeals(self.USER).count())
        lmeal = user_meal.load_lmeals(self.USER).first()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/my_meal/%s/" % lmeal.external_id)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_SUCCESS_MEAL_SAVE, messages)
