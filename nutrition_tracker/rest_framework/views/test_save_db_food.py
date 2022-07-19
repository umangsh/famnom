from __future__ import annotations

from http import HTTPStatus

from django.urls import reverse
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from nutrition_tracker.rest_framework.views import APISaveDBFood
from nutrition_tracker.tests import constants as test_constants
from nutrition_tracker.tests import objects as test_objects


class TestViewsAPISaveDBFood(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.DB_FOOD = test_objects.get_db_food()
        cls.USER = test_objects.get_user()
        cls.API_KEY = test_objects.get_api_key()

    def test_unauthorized_post_fails(self):
        factory = APIRequestFactory()
        view = APISaveDBFood.as_view()

        request = factory.post(reverse("api_save_db_food"), {"id": self.DB_FOOD.external_id})
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_save_db_food_authorized_no_api_key_fails(self):
        factory = APIRequestFactory()
        view = APISaveDBFood.as_view()

        request = factory.post(reverse("api_save_db_food"), {"id": self.DB_FOOD.external_id})
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_save_db_food_authorized_request(self):
        factory = APIRequestFactory()
        view = APISaveDBFood.as_view()

        request = factory.post(
            reverse("api_save_db_food"), {"id": self.DB_FOOD.external_id}, HTTP_X_API_KEY=self.API_KEY
        )
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_save_db_food_authorized_request_bad_id(self):
        factory = APIRequestFactory()
        view = APISaveDBFood.as_view()

        request = factory.post(reverse("api_save_db_food"), {"id": "badid"}, HTTP_X_API_KEY=self.API_KEY)
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_save_db_food_authorized_request_no_id(self):
        factory = APIRequestFactory()
        view = APISaveDBFood.as_view()

        request = factory.post(reverse("api_save_db_food"), HTTP_X_API_KEY=self.API_KEY)
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_save_db_food_authorized_request_id_not_found(self):
        factory = APIRequestFactory()
        view = APISaveDBFood.as_view()

        request = factory.post(
            reverse("api_save_db_food"), {"id": test_constants.TEST_UUID_2}, HTTP_X_API_KEY=self.API_KEY
        )
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
