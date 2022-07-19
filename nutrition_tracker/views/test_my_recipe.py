from __future__ import annotations

from http import HTTPStatus

from django.contrib.messages import get_messages
from django.test import TestCase, override_settings
from django.urls import reverse

from nutrition_tracker.constants import constants
from nutrition_tracker.tests import constants as test_constants
from nutrition_tracker.tests import objects as test_objects
from nutrition_tracker.tests import utils as test_utils


class TestViewsMyRecipe(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_RECIPE = test_objects.get_recipe()
        test_objects.get_user_recipe_portion()
        lfood = test_objects.get_user_ingredient()
        test_objects.get_user_food_portion()
        test_objects.get_user_food_nutrient()
        ufm = test_objects.get_user_food_membership(cls.USER_RECIPE, lfood)
        test_objects.get_user_food_membership_portion(ufm)
        test_objects.get_nutrient_preference()

    def test_recipe_logged_out_redirects(self):
        response = self.client.get(reverse("my_recipe", kwargs={"id": test_constants.TEST_UUID}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/accounts/login/?next=/my_recipe/%s/" % test_constants.TEST_UUID)

    def test_recipe_logged_in_not_found(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("my_recipe", kwargs={"id": test_constants.TEST_UUID}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/my_recipes/")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_ERROR_MISSING_RECIPE, messages)

    @override_settings(DEBUG=False)
    @test_utils.prevent_request_warnings
    def test_recipe_bad_id(self):
        response = self.client.get("/my_recipe/123")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, "errors/404.html")

    def test_recipe_found_logged_in(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("my_recipe", kwargs={"id": self.USER_RECIPE.external_id}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "nutrition_tracker/my_recipe.html")
        self.assertIsNone(response.context["lfood"])
        self.assertIsNone(response.context["cfood"])
        self.assertEqual(response.context["lrecipe"], self.USER_RECIPE)
        self.assertIsNone(response.context["lmeal"])
        self.assertTrue(response.context["lfoods"])
        self.assertFalse(response.context["member_recipes"])
        self.assertFalse(response.context["lmeals"])
        self.assertTrue(response.context["food_nutrients"])
        self.assertTrue(response.context["food_portions"])
        self.assertTrue(response.context["nutrient_preferences"])
