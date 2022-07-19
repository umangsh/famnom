from __future__ import annotations

import datetime
from http import HTTPStatus

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from nutrition_tracker.constants import constants
from nutrition_tracker.tests import objects as test_objects


class TestViewsMyNutrition(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        test_objects.get_nutrient_preference()

    def test_logged_out_redirects(self):
        response = self.client.get(reverse("my_nutrition"), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/accounts/login/?next=/my_nutrition/")

    def test_logged_in_page_load_success(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("my_nutrition"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "nutrition_tracker/my_nutrition.html")
        self.assertTrue(response.context["fda_nutrients"])

    def test_logged_in_save_success(self):
        self.client.login(email="user@famnom.com", password="password")
        new_date_of_birth = datetime.date(1953, 1, 4)
        response = self.client.post(reverse("my_nutrition"), {"date_of_birth": new_date_of_birth}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/my_nutrition/")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_SUCCESS_NUTRITION_SAVE, messages)
        self.USER.refresh_from_db()
        self.assertEqual(self.USER.date_of_birth, new_date_of_birth)
