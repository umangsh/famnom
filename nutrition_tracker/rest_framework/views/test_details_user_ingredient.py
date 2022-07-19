from __future__ import annotations

from http import HTTPStatus

from django.urls import reverse
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from nutrition_tracker.rest_framework.views import APIDetailsUserIngredient
from nutrition_tracker.tests import objects as test_objects


class TestViewsAPIDetailsUserIngredient(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_FOOD = test_objects.get_user_ingredient()
        cls.USER = test_objects.get_user()
        cls.API_KEY = test_objects.get_api_key()

    def test_unauthorized_get_fails(self):
        factory = APIRequestFactory()
        view = APIDetailsUserIngredient.as_view()

        request = factory.get(reverse("api_details_user_ingredient", kwargs={"id": self.USER_FOOD.external_id}))
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_get_useringredient_authorized_no_api_key_fails(self):
        factory = APIRequestFactory()
        view = APIDetailsUserIngredient.as_view()

        request = factory.get(reverse("api_details_user_ingredient", kwargs={"id": self.USER_FOOD.external_id}))
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_get_useringredient_authorized_request(self):
        factory = APIRequestFactory()
        view = APIDetailsUserIngredient.as_view()

        request = factory.get(
            reverse("api_details_user_ingredient", kwargs={"id": self.USER_FOOD.external_id}),
            HTTP_X_API_KEY=self.API_KEY,
        )
        force_authenticate(request, user=self.USER)
        response = view(request, id=self.USER_FOOD.external_id)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data["external_id"], str(self.USER_FOOD.external_id))
        self.assertEqual(response.data["display_name"], self.USER_FOOD.display_name)
