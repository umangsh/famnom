from __future__ import annotations

from http import HTTPStatus

from django.urls import reverse
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from nutrition_tracker.constants import constants
from nutrition_tracker.rest_framework.views import APINutrient
from nutrition_tracker.tests import objects as test_objects


class TestViewsAPINutrient(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.API_KEY = test_objects.get_api_key()
        cls.NUTRIENT_ID = constants.ENERGY_NUTRIENT_ID

    def test_unauthorized_get_fails(self):
        factory = APIRequestFactory()
        view = APINutrient.as_view()

        request = factory.get(reverse("api_nutrient", kwargs={"id": self.NUTRIENT_ID}))
        response = view(request, id=self.NUTRIENT_ID)

        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_authorized_post_no_api_key_fails(self):
        factory = APIRequestFactory()
        view = APINutrient.as_view()

        request = factory.get(reverse("api_nutrient", kwargs={"id": self.NUTRIENT_ID}))
        force_authenticate(request, user=self.USER)
        response = view(request, id=self.NUTRIENT_ID)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_log_authorized_request(self):
        factory = APIRequestFactory()
        view = APINutrient.as_view()

        request = factory.get(reverse("api_nutrient", kwargs={"id": self.NUTRIENT_ID}), HTTP_X_API_KEY=self.API_KEY)
        force_authenticate(request, user=self.USER)
        response = view(request, id=self.NUTRIENT_ID)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue("name" in response.data)
        self.assertTrue("description" in response.data)
        self.assertTrue("top_cfoods" in response.data)
        self.assertTrue("recent_lfoods" in response.data)
