from __future__ import annotations

from http import HTTPStatus

from django.urls import reverse
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from nutrition_tracker.rest_framework.views import APISearchResults
from nutrition_tracker.tests import objects as test_objects


class TestViewsAPISearchResults(APITestCase):
    @classmethod
    def setUpTestData(cls):
        test_objects.index_cfood()
        cls.USER = test_objects.get_user()
        cls.API_KEY = test_objects.get_api_key()

    def test_get_results_unauthorized_fails(self):
        factory = APIRequestFactory()
        view = APISearchResults.as_view()

        request = factory.get(reverse("api_search"))
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_get_results_authorized_no_api_key_fails(self):
        factory = APIRequestFactory()
        view = APISearchResults.as_view()

        request = factory.get(reverse("api_search"))
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_get_results_authorized_empty_query(self):
        factory = APIRequestFactory()
        view = APISearchResults.as_view()

        request = factory.get(reverse("api_search"), HTTP_X_API_KEY=self.API_KEY)
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data["count"], 0)

    def test_get_results_authorized_exact_query_match(self):
        factory = APIRequestFactory()
        view = APISearchResults.as_view()

        request = factory.get(reverse("api_search"), {"q": "test"}, HTTP_X_API_KEY=self.API_KEY)
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["dname"], "test")

    def test_get_results_authorized_query_match(self):
        factory = APIRequestFactory()
        view = APISearchResults.as_view()

        request = factory.get(reverse("api_search"), {"q": "tESt"}, HTTP_X_API_KEY=self.API_KEY)
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["dname"], "test")

    def test_get_results_authorized_query_no_match(self):
        factory = APIRequestFactory()
        view = APISearchResults.as_view()

        request = factory.get(reverse("api_search"), {"q": "nomatch"}, HTTP_X_API_KEY=self.API_KEY)
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data["count"], 0)
