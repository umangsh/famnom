from __future__ import annotations

from http import HTTPStatus

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from nutrition_tracker.constants import constants
from nutrition_tracker.tests import objects as test_objects


class TestViewsMyBarcodeAjax(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        test_objects.verify_user(cls.USER)

    def test_get_non_ajax_request_logged_out_redirects(self):
        response = self.client.get(reverse("my_barcode_ajax", kwargs={"c": "abc"}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/accounts/login/?next=/my_barcode_ajax/abc/")

    def test_get_non_ajax_request_logged_in_redirects(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("my_barcode_ajax", kwargs={"c": "abc"}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_ERROR_UNSUPPORTED_ACTION, messages)

    def test_get_ajax_request_logged_in_user_food(self):
        lfood = test_objects.get_user_ingredient()
        test_objects.get_user_branded_food()

        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(
            reverse("my_barcode_ajax", kwargs={"c": "user_upc"}), HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertJSONEqual(response.content.decode("utf8"), {"url": "/my_ingredient/%s/" % lfood.external_id})

    def test_get_ajax_request_logged_in_db_food(self):
        cfood = test_objects.get_db_food()
        test_objects.index_cfood()

        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(
            reverse("my_barcode_ajax", kwargs={"c": "db_upc"}), HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertJSONEqual(response.content.decode("utf8"), {"url": "/my_food/%s/" % cfood.external_id})

    def test_get_ajax_request_logged_in_no_results(self):
        test_objects.get_user_ingredient()
        test_objects.get_user_branded_food()
        test_objects.index_cfood()

        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(
            reverse("my_barcode_ajax", kwargs={"c": "unknownupc"}), HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertJSONEqual(response.content.decode("utf8"), {})
