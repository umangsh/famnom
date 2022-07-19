from __future__ import annotations

from http import HTTPStatus

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from nutrition_tracker.biz import user
from nutrition_tracker.constants import constants
from nutrition_tracker.models import user_food_membership, user_ingredient
from nutrition_tracker.tests import constants as test_constants
from nutrition_tracker.tests import objects as test_objects


class TestViewsMyFoodDelete(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.USER_FOOD = test_objects.get_user_ingredient()

    def test_ingredient_logged_out_get_redirects(self):
        response = self.client.get(reverse("my_food_delete"), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/accounts/login/?next=/my_food_delete/")

    def test_ingredient_logged_in_get_redirects(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("my_food_delete"), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/my_foods/")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_ERROR_UNSUPPORTED_ACTION, messages)

    def test_ingredient_logged_out_post_redirects(self):
        response = self.client.post(reverse("my_food_delete"), {"id": test_constants.TEST_UUID}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/accounts/login/?next=/my_food_delete/")

    def test_ingredient_logged_in_post_missing_id(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.post(reverse("my_food_delete"), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/my_foods/")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_ERROR_INVALID_ID, messages)

    def test_ingredient_logged_in_post_missing_object(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.post(reverse("my_food_delete"), {"id": test_constants.TEST_UUID}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/my_foods/")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_ERROR_MISSING_FOOD, messages)

    def test_ingredient_logged_in_non_owner_fails(self):
        luser_2 = test_objects.get_user_2()
        user.create_family(self.USER, luser_2.email)
        self.USER.refresh_from_db()
        luser_2.refresh_from_db()

        self.client.login(email=luser_2.email, password="password_2")
        response = self.client.post(reverse("my_food_delete"), {"id": self.USER_FOOD.external_id}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/my_foods/")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_ERROR_DELETE_NOT_ALLOWED, messages)
        self.assertEqual(1, user_ingredient.load_lfoods(self.USER).count())

    def test_ingredient_logged_in_post_success(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.post(reverse("my_food_delete"), {"id": self.USER_FOOD.external_id}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/my_foods/")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_SUCCESS_FOOD_DELETE, messages)
        self.assertEqual(0, user_ingredient.load_lfoods(self.USER).count())

    def test_ingredient_in_meal_logged_in_non_owner_fails(self):
        luser_2 = test_objects.get_user_2()
        lfood_2 = test_objects.get_user_2_ingredient()
        lmeal_2 = test_objects.get_meal_2_today_1()
        ufm = test_objects.get_user_2_food_membership(lmeal_2, lfood_2)
        test_objects.get_user_2_food_membership_portion(ufm)

        self.client.login(email="user@famnom.com", password="password")
        response = self.client.post(
            reverse("my_food_delete"), {"id": self.USER_FOOD.external_id, "mid": ufm.external_id}, follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/my_foods/")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_ERROR_DELETE_NOT_ALLOWED, messages)
        self.assertEqual(1, user_food_membership.load_lmemberships(luser_2).count())

    def test_ingredient_in_meal_logged_in_post_success(self):
        lmeal = test_objects.get_meal_today_1()
        ufm = test_objects.get_user_food_membership(lmeal, self.USER_FOOD)
        test_objects.get_user_food_membership_portion(ufm)

        self.client.login(email="user@famnom.com", password="password")
        response = self.client.post(
            reverse("my_food_delete"), {"id": self.USER_FOOD.external_id, "mid": ufm.external_id}, follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/my_foods/")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_SUCCESS_FOOD_DELETE, messages)
        self.assertEqual(0, user_food_membership.load_lmemberships(self.USER).count())
