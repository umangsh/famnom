from __future__ import annotations

from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from nutrition_tracker.tests import objects as test_objects


class TestViewsMyMeals(TestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.USER_MEAL_1 = test_objects.get_meal_today_1()
        cls.USER_MEAL_2 = test_objects.get_meal_today_2()
        cls.USER_MEAL_3 = test_objects.get_meal_yesterday_1()
        cls.USER_MEAL_4 = test_objects.get_meal_yesterday_2()

    def test_logged_out_redirects(self):
        response = self.client.get(reverse("my_meals"), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/accounts/login/?next=/my_meals/")

    def test_logged_in_success(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("my_meals"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(4, len(response.context["lmeals"]))

    def test_ajax_logged_in_success(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get("/my_meals/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        expected_output = {
            "results": [
                {"id": "%s" % self.USER_MEAL_2.external_id, "text": "Lunch: Today"},
                {"id": "%s" % self.USER_MEAL_1.external_id, "text": "Breakfast: Today"},
                {"id": "%s" % self.USER_MEAL_4.external_id, "text": "Lunch: Yesterday"},
                {"id": "%s" % self.USER_MEAL_3.external_id, "text": "Breakfast: Yesterday"},
            ],
            "pagination": {"more": False},
        }
        self.assertJSONEqual(response.content.decode("utf8"), expected_output)
