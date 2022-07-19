from __future__ import annotations

from http import HTTPStatus

from django.contrib.messages import get_messages
from django.test import TransactionTestCase
from django.urls import reverse

from nutrition_tracker.constants import constants
from nutrition_tracker.tests import constants as test_constants
from nutrition_tracker.tests import objects as test_objects


class TestViewsMyServingAjax(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.USER = test_objects.get_user()
        test_objects.verify_user(self.USER)

    def test_get_non_ajax_request_logged_out_redirects(self):
        response = self.client.get(reverse("my_serving_ajax", kwargs={"id": test_constants.TEST_UUID}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/accounts/login/?next=/my_serving_ajax/%s/" % test_constants.TEST_UUID)

    def test_get_non_ajax_request_logged_in_redirects(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("my_serving_ajax", kwargs={"id": test_constants.TEST_UUID}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_ERROR_UNSUPPORTED_ACTION, messages)

    def test_get_ajax_request_logged_in_food(self):
        lfood = test_objects.get_user_ingredient()
        lfood_portion = test_objects.get_user_food_portion()
        cfood_portion = test_objects.get_db_food_portion()

        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(
            reverse("my_serving_ajax", kwargs={"id": lfood.external_id}), HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        expected_output = [
            [str(lfood_portion.external_id), {"label": "83g", "data-gm-wt": 83.0, "data-wt-unit": "g"}],
            [str(cfood_portion.external_id), {"label": "100g", "data-gm-wt": 100.0, "data-wt-unit": "g"}],
            [-1, {"label": "100g", "data-gm-wt": 100, "data-wt-unit": "g"}],
            [-2, {"label": "1g", "data-gm-wt": 1, "data-wt-unit": "g"}],
            [-3, {"label": "1oz", "data-gm-wt": 28.3495, "data-wt-unit": "g"}],
        ]
        self.assertJSONEqual(response.content.decode("utf8"), expected_output)

    def test_get_ajax_request_logged_in_recipe(self):
        lrecipe = test_objects.get_recipe()
        lfood_portion = test_objects.get_user_recipe_portion()

        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(
            reverse("my_serving_ajax", kwargs={"id": lrecipe.external_id}), HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        expected_output = [
            [str(lfood_portion.external_id), {"label": "200g", "data-gm-wt": 200.0, "data-wt-unit": "g"}],
            [-1, {"label": "100g", "data-gm-wt": 100, "data-wt-unit": "g"}],
            [-2, {"label": "1g", "data-gm-wt": 1, "data-wt-unit": "g"}],
            [-3, {"label": "1oz", "data-gm-wt": 28.3495, "data-wt-unit": "g"}],
        ]
        self.assertJSONEqual(response.content.decode("utf8"), expected_output)

    def test_get_ajax_request_logged_in_no_results(self):
        test_objects.get_user_ingredient()
        test_objects.get_user_food_portion()
        test_objects.get_db_food_portion()
        test_objects.get_recipe()
        test_objects.get_user_recipe_portion()

        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(
            reverse("my_serving_ajax", kwargs={"id": test_constants.TEST_UUID}), HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertJSONEqual(response.content.decode("utf8"), {})
