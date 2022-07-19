from __future__ import annotations

from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from nutrition_tracker.tests import objects as test_objects


class TestViewsMyFoods(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.USER_FOOD_1 = test_objects.get_user_ingredient()
        cls.USER_FOOD_2 = test_objects.get_user_ingredient_2()
        test_objects.get_user_preference()

    def test_logged_out_redirects(self):
        response = self.client.get(reverse("my_foods"), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/accounts/login/?next=/my_foods/")

    def test_logged_in_success(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("my_foods"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(2, response.context["lfoods"].count())

    def test_logged_in_success_query(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get("/my_foods/?q=2")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(1, response.context["lfoods"].count())

    def test_logged_in_success_query_no_results(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get("/my_foods/?q=noresults")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(response.context["lfoods"].exists())

    def test_logged_in_success_preference_flags(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get("/my_foods/?fs=is_available")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(1, response.context["lfoods"].count())

    def test_logged_in_success_preference_bad_flag_ignored(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get("/my_foods/?fs=unknown_flag")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(2, response.context["lfoods"].count())

    def test_logged_in_success_all_set(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get("/my_foods/?q=test&fs=is_available&fn=is_not_allowed")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(1, response.context["lfoods"].count())

    def test_logged_in_success_all_set_no_results(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get("/my_foods/?q=test&fs=is_not_allowed")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(response.context["lfoods"].exists())

    def test_ajax_logged_in_success_preference_bad_flag_ignored(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get("/my_foods/?q=test&fs=unknown_flag", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        expected_output = {
            "results": [
                {"id": "%s" % self.USER_FOOD_1.external_id, "text": "test"},
                {"id": "%s" % self.USER_FOOD_2.external_id, "text": "test_2"},
            ],
            "pagination": {"more": False},
        }
        self.assertJSONEqual(response.content.decode("utf8"), expected_output)
