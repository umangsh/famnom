from __future__ import annotations

from http import HTTPStatus

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from nutrition_tracker.constants import constants
from nutrition_tracker.tests import constants as test_constants
from nutrition_tracker.tests import objects as test_objects


class TestViewsMyNutrientAjax(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        test_objects.verify_user(cls.USER)

    def test_get_non_ajax_request_logged_out_redirects(self):
        response = self.client.get(reverse("my_nutrient_ajax", kwargs={"id": test_constants.TEST_UUID}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/accounts/login/?next=/my_nutrient_ajax/%s/" % test_constants.TEST_UUID)

    def test_get_non_ajax_request_logged_in_redirects(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("my_nutrient_ajax", kwargs={"id": test_constants.TEST_UUID}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_ERROR_UNSUPPORTED_ACTION, messages)

    def test_get_ajax_request_logged_in_food(self):
        lfood = test_objects.get_user_ingredient()
        test_objects.get_user_food_nutrient()
        test_objects.get_user_food_nutrient_2()
        test_objects.get_db_food_nutrient()
        test_objects.get_db_food_nutrient_2()

        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(
            reverse("my_nutrient_ajax", kwargs={"id": lfood.external_id}), HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        expected_output = [
            {"nutrient_id": 1008, "amount": 100.0},
            {"nutrient_id": 1004, "amount": 37.0},
            {"nutrient_id": 1258, "amount": None},
            {"nutrient_id": 1257, "amount": None},
            {"nutrient_id": 1293, "amount": None},
            {"nutrient_id": 1292, "amount": None},
            {"nutrient_id": 1253, "amount": None},
            {"nutrient_id": 1093, "amount": None},
            {"nutrient_id": 1099, "amount": None},
            {"nutrient_id": 1005, "amount": None},
            {"nutrient_id": 1079, "amount": None},
            {"nutrient_id": 1082, "amount": None},
            {"nutrient_id": 1084, "amount": None},
            {"nutrient_id": 1063, "amount": None},
            {"nutrient_id": 1235, "amount": None},
            {"nutrient_id": 1086, "amount": None},
            {"nutrient_id": 1003, "amount": 54.0},
            {"nutrient_id": 1114, "amount": None},
            {"nutrient_id": 1087, "amount": None},
            {"nutrient_id": 1089, "amount": None},
            {"nutrient_id": 1092, "amount": None},
            {"nutrient_id": 1106, "amount": None},
            {"nutrient_id": 1162, "amount": None},
            {"nutrient_id": 1109, "amount": None},
            {"nutrient_id": 1183, "amount": None},
            {"nutrient_id": 1165, "amount": None},
            {"nutrient_id": 1166, "amount": None},
            {"nutrient_id": 1167, "amount": None},
            {"nutrient_id": 1175, "amount": None},
            {"nutrient_id": 1177, "amount": None},
            {"nutrient_id": 1178, "amount": None},
            {"nutrient_id": 1176, "amount": None},
            {"nutrient_id": 1170, "amount": None},
            {"nutrient_id": 1091, "amount": None},
            {"nutrient_id": 1100, "amount": None},
            {"nutrient_id": 1090, "amount": None},
            {"nutrient_id": 1095, "amount": None},
            {"nutrient_id": 1103, "amount": None},
            {"nutrient_id": 1098, "amount": None},
            {"nutrient_id": 1101, "amount": None},
            {"nutrient_id": 1096, "amount": None},
            {"nutrient_id": 1102, "amount": None},
            {"nutrient_id": 1180, "amount": None},
        ]
        self.assertJSONEqual(response.content.decode("utf8"), expected_output)

    def test_get_ajax_request_logged_in_recipe(self):
        lrecipe = test_objects.get_recipe()
        test_objects.get_user_recipe_portion()
        lfood = test_objects.get_user_ingredient()
        test_objects.get_user_food_nutrient()
        ufm = test_objects.get_user_food_membership(lrecipe, lfood)
        test_objects.get_user_food_membership_portion(ufm)

        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(
            reverse("my_nutrient_ajax", kwargs={"id": lrecipe.external_id}), HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        expected_output = [
            {"nutrient_id": 1008, "amount": 25.0},
            {"nutrient_id": 1004, "amount": None},
            {"nutrient_id": 1258, "amount": None},
            {"nutrient_id": 1257, "amount": None},
            {"nutrient_id": 1293, "amount": None},
            {"nutrient_id": 1292, "amount": None},
            {"nutrient_id": 1253, "amount": None},
            {"nutrient_id": 1093, "amount": None},
            {"nutrient_id": 1099, "amount": None},
            {"nutrient_id": 1005, "amount": None},
            {"nutrient_id": 1079, "amount": None},
            {"nutrient_id": 1082, "amount": None},
            {"nutrient_id": 1084, "amount": None},
            {"nutrient_id": 1063, "amount": None},
            {"nutrient_id": 1235, "amount": None},
            {"nutrient_id": 1086, "amount": None},
            {"nutrient_id": 1003, "amount": None},
            {"nutrient_id": 1114, "amount": None},
            {"nutrient_id": 1087, "amount": None},
            {"nutrient_id": 1089, "amount": None},
            {"nutrient_id": 1092, "amount": None},
            {"nutrient_id": 1106, "amount": None},
            {"nutrient_id": 1162, "amount": None},
            {"nutrient_id": 1109, "amount": None},
            {"nutrient_id": 1183, "amount": None},
            {"nutrient_id": 1165, "amount": None},
            {"nutrient_id": 1166, "amount": None},
            {"nutrient_id": 1167, "amount": None},
            {"nutrient_id": 1175, "amount": None},
            {"nutrient_id": 1177, "amount": None},
            {"nutrient_id": 1178, "amount": None},
            {"nutrient_id": 1176, "amount": None},
            {"nutrient_id": 1170, "amount": None},
            {"nutrient_id": 1091, "amount": None},
            {"nutrient_id": 1100, "amount": None},
            {"nutrient_id": 1090, "amount": None},
            {"nutrient_id": 1095, "amount": None},
            {"nutrient_id": 1103, "amount": None},
            {"nutrient_id": 1098, "amount": None},
            {"nutrient_id": 1101, "amount": None},
            {"nutrient_id": 1096, "amount": None},
            {"nutrient_id": 1102, "amount": None},
            {"nutrient_id": 1180, "amount": None},
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
            reverse("my_nutrient_ajax", kwargs={"id": test_constants.TEST_UUID}),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertJSONEqual(response.content.decode("utf8"), {})
