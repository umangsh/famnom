from __future__ import annotations

import json
from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from nutrition_tracker.tests import objects as test_objects


class TestViewsMyRecipes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.USER_RECIPE_1 = test_objects.get_recipe()
        cls.USER_RECIPE_2 = test_objects.get_recipe_2()
        test_objects.get_user_recipe_preference()

    def test_logged_out_redirects(self):
        response = self.client.get(reverse("my_recipes"), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/accounts/login/?next=/my_recipes/")

    def test_logged_in_success(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("my_recipes"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(2, response.context["lrecipes"].count())

    def test_logged_in_success_query(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get("/my_recipes/?q=2")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(1, response.context["lrecipes"].count())

    def test_logged_in_success_query_no_results(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get("/my_recipes/?q=noresults")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(response.context["lrecipes"].exists())

    def test_logged_in_success_preference_flags(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get("/my_recipes/?fs=is_available")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(1, response.context["lrecipes"].count())

    def test_logged_in_success_preference_bad_flag_ignored(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get("/my_recipes/?fs=unknown_flag")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(2, response.context["lrecipes"].count())

    def test_logged_in_success_all_set(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get("/my_recipes/?q=test&fs=is_available&fn=is_not_allowed")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(1, response.context["lrecipes"].count())

    def test_logged_in_success_all_set_no_results(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get("/my_recipes/?q=test&fs=is_not_allowed")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(response.context["lrecipes"].exists())

    def test_ajax_logged_in_success_preference_bad_flag_ignored(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get("/my_recipes/?q=test&fs=unknown_flag", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response = json.loads(response.content.decode("utf8"))
        self.assertEqual(2, len(response["results"]))
