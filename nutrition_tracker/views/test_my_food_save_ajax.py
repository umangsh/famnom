from __future__ import annotations

from http import HTTPStatus

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from nutrition_tracker.constants import constants
from nutrition_tracker.models import user_ingredient
from nutrition_tracker.tests import constants as test_constants
from nutrition_tracker.tests import objects as test_objects
from nutrition_tracker.tests import utils as test_utils


class TestViewsMyFoodSaveAjax(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.DB_FOOD = test_objects.get_db_food()

    def test_logged_out_get_redirects(self):
        response = self.client.get(reverse("my_food_save_ajax"), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/accounts/login/?next=/my_food_save_ajax/")

    def test_logged_in_get_redirects(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("my_food_save_ajax"), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_ERROR_UNSUPPORTED_ACTION, messages)

    def test_logged_out_post_redirects(self):
        response = self.client.post(reverse("my_food_save_ajax"), {"id": test_constants.TEST_UUID}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/accounts/login/?next=/my_food_save_ajax/")

    def test_logged_in_post_non_ajax_redirects(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.post(reverse("my_food_save_ajax"), {"id": test_constants.TEST_UUID}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/search/")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_ERROR_UNSUPPORTED_ACTION, messages)

    @test_utils.prevent_request_warnings
    def test_logged_in_post_ajax_invalid_id(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.post(reverse("my_food_save_ajax"), {"id": 123}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertJSONEqual(response.content.decode("utf8"), {})

    def test_logged_in_post_ajax_no_cfood_success(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.post(
            reverse("my_food_save_ajax"), {"id": test_constants.TEST_UUID}, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertJSONEqual(response.content.decode("utf8"), {})
        self.assertEqual(0, user_ingredient.load_lfoods(self.USER).count())

    def test_logged_in_post_ajax_no_lfood_success(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.post(
            reverse("my_food_save_ajax"), {"id": self.DB_FOOD.external_id}, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertJSONEqual(response.content.decode("utf8"), {})
        self.assertEqual(1, user_ingredient.load_lfoods(self.USER).count())

    def test_logged_in_post_ajax_lfood_success(self):
        test_objects.get_user_ingredient()
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.post(
            reverse("my_food_save_ajax"), {"id": self.DB_FOOD.external_id}, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertJSONEqual(response.content.decode("utf8"), {})
        self.assertEqual(1, user_ingredient.load_lfoods(self.USER).count())
