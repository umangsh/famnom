from __future__ import annotations

from http import HTTPStatus
from unittest.mock import patch

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from nutrition_tracker.constants import constants
from nutrition_tracker.tests import objects as test_objects


def load_lfoods_for_lparents(*args, **kwargs):
    return [test_objects.get_user_ingredient()]


class TestViewsMySuggestedFoodsAjax(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_objects.get_user()
        test_objects.get_user_ingredient()

    def test_non_ajax_redirects(self):
        response = self.client.get(reverse("my_suggested_foods_ajax"), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_ERROR_UNSUPPORTED_ACTION, messages)

    def test_ajax_logged_out_empty(self):
        response = self.client.get(reverse("my_suggested_foods_ajax"), HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "nutrition_tracker/my_suggested_foods_ajax.html")
        self.assertFalse(response.context["suggested_lobjects"])

    @patch(target="nutrition_tracker.logic.data_loaders.load_lfoods_for_lparents", wraps=load_lfoods_for_lparents)
    def test_ajax_logged_in(self, mock_load_lfoods_for_lparents):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("my_suggested_foods_ajax"), HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "nutrition_tracker/my_suggested_foods_ajax.html")
        self.assertTrue(response.context["suggested_lobjects"])
