from __future__ import annotations

from http import HTTPStatus

from django.urls import reverse
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from nutrition_tracker.rest_framework.views import APIAppConstants
from nutrition_tracker.tests import objects as test_objects


class TestViewsAPIAppConstants(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.API_KEY = test_objects.get_api_key()

    def test_unauthorized_get_fails(self):
        factory = APIRequestFactory()
        view = APIAppConstants.as_view()

        request = factory.get(reverse("api_app_constants"))
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_get_nutrition_authorized_no_api_key_fails(self):
        factory = APIRequestFactory()
        view = APIAppConstants.as_view()

        request = factory.get(reverse("api_app_constants"))
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_get_nutrition_authorized_success(self):
        factory = APIRequestFactory()
        view = APIAppConstants.as_view()

        request = factory.get(reverse("api_app_constants"), HTTP_X_API_KEY=self.API_KEY)
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.data)
