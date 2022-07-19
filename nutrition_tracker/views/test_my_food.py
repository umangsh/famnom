from __future__ import annotations

from http import HTTPStatus

from django.contrib.messages import get_messages
from django.test import TestCase, override_settings
from django.urls import reverse

from nutrition_tracker.constants import constants
from nutrition_tracker.tests import constants as test_constants
from nutrition_tracker.tests import objects as test_objects
from nutrition_tracker.tests import utils as test_utils


class TestViewsMyFood(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.DB_FOOD = test_objects.get_db_food()
        test_objects.get_db_food_portion()
        test_objects.get_db_food_nutrient()
        test_objects.get_nutrient_preference()

    def test_food_not_found(self):
        response = self.client.get(reverse("my_food", kwargs={"id": test_constants.TEST_UUID}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/search/")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_ERROR_MISSING_FOOD, messages)

    @override_settings(DEBUG=False)
    @test_utils.prevent_request_warnings
    def test_food_bad_id(self):
        response = self.client.get("/my_food/123")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, "errors/404.html")

    def test_food_found_logged_out(self):
        response = self.client.get(reverse("my_food", kwargs={"id": self.DB_FOOD.external_id}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "nutrition_tracker/my_food.html")
        self.assertIsNone(response.context["lfood"])
        self.assertEqual(response.context["cfood"], self.DB_FOOD)
        self.assertIsNone(response.context["lrecipe"])
        self.assertIsNone(response.context["lmeal"])
        self.assertFalse(response.context["lfoods"])
        self.assertFalse(response.context["member_recipes"])
        self.assertFalse(response.context["lmeals"])
        self.assertTrue(response.context["food_nutrients"])
        self.assertTrue(response.context["food_portions"])
        self.assertFalse(response.context["nutrient_preferences"])

    def test_food_found_logged_in(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("my_food", kwargs={"id": self.DB_FOOD.external_id}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "nutrition_tracker/my_food.html")
        self.assertIsNone(response.context["lfood"])
        self.assertEqual(response.context["cfood"], self.DB_FOOD)
        self.assertIsNone(response.context["lrecipe"])
        self.assertIsNone(response.context["lmeal"])
        self.assertFalse(response.context["lfoods"])
        self.assertFalse(response.context["member_recipes"])
        self.assertFalse(response.context["lmeals"])
        self.assertTrue(response.context["food_nutrients"])
        self.assertTrue(response.context["food_portions"])
        self.assertTrue(response.context["nutrient_preferences"])
