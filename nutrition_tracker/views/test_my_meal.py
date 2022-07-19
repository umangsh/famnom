from __future__ import annotations

from http import HTTPStatus

from django.contrib.messages import get_messages
from django.test import TestCase, override_settings
from django.urls import reverse

from nutrition_tracker.constants import constants
from nutrition_tracker.tests import constants as test_constants
from nutrition_tracker.tests import objects as test_objects
from nutrition_tracker.tests import utils as test_utils


class TestViewsMyMeal(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_MEAL = test_objects.get_meal_today_1()
        lfood = test_objects.get_user_ingredient()
        test_objects.get_user_food_portion()
        test_objects.get_user_food_nutrient()
        test_objects.get_nutrient_preference()
        ufm = test_objects.get_user_food_membership(cls.USER_MEAL, lfood)
        test_objects.get_user_food_membership_portion(ufm)
        lrecipe = test_objects.get_recipe()
        ufm = test_objects.get_user_food_membership(cls.USER_MEAL, lrecipe)
        test_objects.get_user_food_membership_portion(ufm)

    def test_meal_logged_out_redirects(self):
        response = self.client.get(reverse("my_meal", kwargs={"id": test_constants.TEST_UUID}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/accounts/login/?next=/my_meal/%s/" % test_constants.TEST_UUID)

    def test_meal_logged_in_not_found(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("my_meal", kwargs={"id": test_constants.TEST_UUID}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/my_meals/")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_ERROR_MISSING_MEAL, messages)

    @override_settings(DEBUG=False)
    @test_utils.prevent_request_warnings
    def test_meal_bad_id(self):
        response = self.client.get("/my_meal/123")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, "errors/404.html")

    def test_meal_found_logged_in(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("my_meal", kwargs={"id": self.USER_MEAL.external_id}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "nutrition_tracker/my_meal.html")
        self.assertIsNone(response.context["lfood"])
        self.assertIsNone(response.context["cfood"])
        self.assertIsNone(response.context["lrecipe"])
        self.assertEqual(response.context["lmeal"], self.USER_MEAL)
        self.assertTrue(response.context["lfoods"])
        self.assertTrue(response.context["member_recipes"])
        self.assertFalse(response.context["lmeals"])
        self.assertTrue(response.context["food_nutrients"])
        self.assertFalse(response.context["food_portions"])
        self.assertTrue(response.context["nutrient_preferences"])
