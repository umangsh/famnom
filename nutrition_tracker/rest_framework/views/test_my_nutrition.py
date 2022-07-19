from __future__ import annotations

from http import HTTPStatus

from django.urls import reverse
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import user_prefs
from nutrition_tracker.rest_framework.views import APIMyNutrition
from nutrition_tracker.tests import objects as test_objects
from nutrition_tracker.utils import form as form_utils


class TestViewsAPIMyNutrition(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.API_KEY = test_objects.get_api_key()

    def test_unauthorized_post_fails(self):
        factory = APIRequestFactory()
        view = APIMyNutrition.as_view()

        request = factory.post(reverse("api_my_nutrition"))
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_authorized_post_no_api_key_fails(self):
        factory = APIRequestFactory()
        view = APIMyNutrition.as_view()

        request = factory.post(reverse("api_my_nutrition"))
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_authorized_request(self):
        factory = APIRequestFactory()
        view = APIMyNutrition.as_view()
        nutrient_field_name = form_utils.get_field_name(constants.ENERGY_NUTRIENT_ID)
        threshold_field_name = form_utils.get_threshold_field_name(constants.ENERGY_NUTRIENT_ID)

        request = factory.post(
            reverse("api_my_nutrition"),
            {
                "date_of_birth": self.USER.date_of_birth,
                nutrient_field_name: constants.Threshold.MAX_VALUE,
                threshold_field_name: 53,
            },
            HTTP_X_API_KEY=self.API_KEY,
        )
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(user_prefs.load_nutrition_preferences(self.USER).count(), 1)
