from __future__ import annotations

from http import HTTPStatus
from unittest.mock import patch

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from nutrition_tracker.constants import constants
from nutrition_tracker.tests import objects as test_objects


def load_cfoods(**kwargs):
    return [test_objects.get_db_food()]


class TestViewsTopFoodsAjax(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()

    def test_non_ajax_redirects(self):
        response = self.client.get(reverse("top_foods_ajax", kwargs={"id": 1}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_ERROR_UNSUPPORTED_ACTION, messages)

    def test_ajax_invalid_nutrient_id(self):
        response = self.client.get(reverse("top_foods_ajax", kwargs={"id": 1}), HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "nutrition_tracker/top_foods_ajax.html")
        self.assertFalse(response.context["top_cfoods"])

    @patch(target="nutrition_tracker.models.db_food.load_cfoods", wraps=load_cfoods)
    def test_ajax_valid_nutrient_id(self, mock_load_cfoods):
        response = self.client.get(
            reverse("top_foods_ajax", kwargs={"id": 1008}), HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "nutrition_tracker/top_foods_ajax.html")
        self.assertTrue(response.context["top_cfoods"])
