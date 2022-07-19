from __future__ import annotations

from http import HTTPStatus

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from nutrition_tracker.constants import constants
from nutrition_tracker.tests import objects as test_objects


class TestViewsMyRecentFoodsAjax(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_objects.get_user()
        lfood = test_objects.get_user_ingredient()
        lmeal = test_objects.get_meal_today_1()
        test_objects.get_user_food_nutrient()
        test_objects.get_user_food_membership(lmeal, lfood)

    def test_non_ajax_redirects(self):
        response = self.client.get(reverse("my_recent_foods_ajax", kwargs={"id": 1}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_ERROR_UNSUPPORTED_ACTION, messages)

    def test_ajax_invalid_nutrient_id(self):
        response = self.client.get(
            reverse("my_recent_foods_ajax", kwargs={"id": 1}), HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "nutrition_tracker/my_recent_foods_ajax.html")
        self.assertFalse(response.context["recent_lfoods"])

    def test_ajax_logged_out_valid_nutrient_id(self):
        response = self.client.get(
            reverse("my_recent_foods_ajax", kwargs={"id": 1008}), HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "nutrition_tracker/my_recent_foods_ajax.html")
        self.assertFalse(response.context["recent_lfoods"])

    def test_ajax_logged_in_invalid_nutrient_id(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(
            reverse("my_recent_foods_ajax", kwargs={"id": 1}), HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "nutrition_tracker/my_recent_foods_ajax.html")
        self.assertFalse(response.context["recent_lfoods"])

    def test_ajax_logged_in_valid_nutrient_id(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(
            reverse("my_recent_foods_ajax", kwargs={"id": 1008}), HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "nutrition_tracker/my_recent_foods_ajax.html")
        self.assertTrue(response.context["recent_lfoods"])
