from __future__ import annotations

from http import HTTPStatus

from django.urls import reverse
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from nutrition_tracker.rest_framework.views import APIMyMeals
from nutrition_tracker.tests import objects as test_objects


class TestViewsAPIMyMeals(APITestCase):
    @classmethod
    def setUpTestData(cls):
        test_objects.get_meal_today_1()
        test_objects.get_meal_today_2()
        cls.USER = test_objects.get_user()
        cls.API_KEY = test_objects.get_api_key()

    def test_get_my_meals_unauthorized_fails(self):
        factory = APIRequestFactory()
        view = APIMyMeals.as_view()

        request = factory.get(reverse("api_my_meals"))
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_get_my_meals_authorized_no_api_key_fails(self):
        factory = APIRequestFactory()
        view = APIMyMeals.as_view()

        request = factory.get(reverse("api_my_meals"))
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_get_my_meals_authorized_with_key_success(self):
        factory = APIRequestFactory()
        view = APIMyMeals.as_view()

        request = factory.get(reverse("api_my_meals"), HTTP_X_API_KEY=self.API_KEY)
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data["count"], 2)
