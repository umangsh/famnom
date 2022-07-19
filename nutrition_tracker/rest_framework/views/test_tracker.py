from __future__ import annotations

from http import HTTPStatus

from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from nutrition_tracker.rest_framework.views import APITracker
from nutrition_tracker.tests import objects as test_objects


class TestViewsAPITracker(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_MEAL = test_objects.get_meal_today_1()
        cls.USER_MEAL_2 = test_objects.get_meal_today_2()
        cls.USER = test_objects.get_user()
        cls.API_KEY = test_objects.get_api_key()
        cls.td = timezone.localdate().strftime("%Y-%m-%d")

    def test_unauthorized_get_fails(self):
        factory = APIRequestFactory()
        view = APITracker.as_view()

        request = factory.get(reverse("api_tracker", kwargs={"td": self.td}))
        response = view(request, td=self.td)

        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_authorized_post_no_api_key_fails(self):
        factory = APIRequestFactory()
        view = APITracker.as_view()

        request = factory.get(reverse("api_tracker", kwargs={"td": self.td}))
        force_authenticate(request, user=self.USER)
        response = view(request, td=self.td)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_log_authorized_request(self):
        factory = APIRequestFactory()
        view = APITracker.as_view()

        request = factory.get(reverse("api_tracker", kwargs={"td": self.td}), HTTP_X_API_KEY=self.API_KEY)
        force_authenticate(request, user=self.USER)
        response = view(request, td=self.td)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue("display_meals" in response.data)
        self.assertTrue("display_nutrients" in response.data)
