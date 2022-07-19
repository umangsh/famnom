from __future__ import annotations

from http import HTTPStatus

from django.contrib.messages import get_messages
from django.test import TestCase, override_settings
from django.urls import reverse

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import data_loaders
from nutrition_tracker.models import user_food_membership, user_food_portion
from nutrition_tracker.tests import constants as test_constants
from nutrition_tracker.tests import objects as test_objects
from nutrition_tracker.tests import utils as test_utils


class TestViewsMyIngredientLog(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.DB_FOOD = test_objects.get_db_food()
        cls.USER_FOOD = test_objects.get_user_ingredient()

    def test_logged_out_redirects(self):
        response = self.client.get(
            reverse("my_ingredient_log", kwargs={"id": self.USER_FOOD.external_id}), follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/accounts/login/?next=/my_ingredient_log/%s/" % self.USER_FOOD.external_id)

    def test_logged_in_not_found_redirects(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("my_ingredient_log", kwargs={"id": test_constants.TEST_UUID}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/my_foods/")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_ERROR_MISSING_FOOD, messages)

    @override_settings(DEBUG=False)
    @test_utils.prevent_request_warnings
    def test_logged_in_bad_id_redirects(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get("/my_ingredient_log/123")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, "errors/404.html")

    def test_logged_in_no_meal_success(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("my_ingredient_log", kwargs={"id": self.USER_FOOD.external_id}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "nutrition_tracker/my_food_log.html")
        self.assertEqual(response.context["lfood"], self.USER_FOOD)
        self.assertEqual(response.context["cfood"], self.DB_FOOD)
        self.assertIsNone(response.context["lrecipe"])
        self.assertIsNone(response.context["lmeal"])
        self.assertFalse(response.context["lfoods"])
        self.assertFalse(response.context["member_recipes"])
        self.assertFalse(response.context["lmeals"])
        self.assertFalse(response.context["food_nutrients"])
        self.assertTrue(response.context["food_portions"])
        self.assertFalse(response.context["nutrient_preferences"])

    def test_logged_in_meal_exists_success(self):
        lmeal = test_objects.get_meal_today_1()
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("my_ingredient_log", kwargs={"id": self.USER_FOOD.external_id}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "nutrition_tracker/my_food_log.html")
        self.assertEqual(response.context["lfood"], self.USER_FOOD)
        self.assertEqual(response.context["cfood"], self.DB_FOOD)
        self.assertIsNone(response.context["lrecipe"])
        self.assertEqual(response.context["lmeal"], lmeal)
        self.assertFalse(response.context["lfoods"])
        self.assertFalse(response.context["member_recipes"])
        self.assertFalse(response.context["lmeals"])
        self.assertFalse(response.context["food_nutrients"])
        self.assertTrue(response.context["food_portions"])
        self.assertFalse(response.context["nutrient_preferences"])

    def test_logged_in_meal_exists_post_success(self):
        lmeal = test_objects.get_meal_today_1()
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.post(
            reverse("my_ingredient_log", kwargs={"id": self.USER_FOOD.external_id}),
            {
                "external_id": self.USER_FOOD.external_id,
                "meal_type": lmeal.meal_type,
                "meal_date": lmeal.meal_date,
                "quantity": 5,
                "serving": -1,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_SUCCESS_FOOD_LOG, messages)
        self.assertEqual(
            1,
            user_food_membership.load_lmemberships(
                self.USER, parent_id=lmeal.id, parent_type_id=data_loaders.get_content_type_meal_id()
            ).count(),
        )
        self.assertEqual(1, user_food_portion.load_lfood_portions(self.USER).count())
