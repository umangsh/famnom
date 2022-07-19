from __future__ import annotations

from http import HTTPStatus

from django.urls import reverse
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from nutrition_tracker.rest_framework.views import APIMyRecipes
from nutrition_tracker.tests import objects as test_objects


class TestViewsAPIMyRecipes(APITestCase):
    @classmethod
    def setUpTestData(cls):
        test_objects.get_recipe()
        test_objects.get_user_recipe_preference()
        test_objects.get_recipe_2()
        cls.USER = test_objects.get_user()
        cls.API_KEY = test_objects.get_api_key()

    def test_get_my_recipes_unauthorized_fails(self):
        factory = APIRequestFactory()
        view = APIMyRecipes.as_view()

        request = factory.get(reverse("api_my_recipes"))
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_get_my_recipes_authorized_no_api_key_fails(self):
        factory = APIRequestFactory()
        view = APIMyRecipes.as_view()

        request = factory.get(reverse("api_my_recipes"))
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_get_my_recipes_authorized_with_key_success(self):
        factory = APIRequestFactory()
        view = APIMyRecipes.as_view()

        request = factory.get(reverse("api_my_recipes"), HTTP_X_API_KEY=self.API_KEY)
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data["count"], 2)

    def test_get_my_recipes_authorized_with_key_query_success(self):
        factory = APIRequestFactory()
        view = APIMyRecipes.as_view()

        request = factory.get(reverse("api_my_recipes"), {"q": "2"}, HTTP_X_API_KEY=self.API_KEY)
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data["count"], 1)

    def test_get_my_recipes_authorized_with_key_flag_set_success(self):
        factory = APIRequestFactory()
        view = APIMyRecipes.as_view()

        request = factory.get(reverse("api_my_recipes"), {"fs": "is_available"}, HTTP_X_API_KEY=self.API_KEY)
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data["count"], 1)
