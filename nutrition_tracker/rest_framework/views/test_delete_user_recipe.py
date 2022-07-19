from __future__ import annotations

from http import HTTPStatus

from django.urls import reverse
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from nutrition_tracker.models import user_recipe
from nutrition_tracker.rest_framework.views import APIDeleteUserRecipe
from nutrition_tracker.tests import constants as test_constants
from nutrition_tracker.tests import objects as test_objects


class TestViewsAPIDeleteUserRecipe(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_RECIPE = test_objects.get_recipe()
        cls.USER = test_objects.get_user()
        cls.API_KEY = test_objects.get_api_key()

    def test_unauthorized_post_fails(self):
        factory = APIRequestFactory()
        view = APIDeleteUserRecipe.as_view()

        request = factory.post(reverse("api_delete_user_recipe", kwargs={"id": self.USER_RECIPE.external_id}))
        response = view(request, id=self.USER_RECIPE.external_id)

        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_delete_user_recipe_authorized_no_api_key_fails(self):
        factory = APIRequestFactory()
        view = APIDeleteUserRecipe.as_view()

        request = factory.post(reverse("api_delete_user_recipe", kwargs={"id": self.USER_RECIPE.external_id}))
        force_authenticate(request, user=self.USER)
        response = view(request, id=self.USER_RECIPE.external_id)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_delete_user_recipe_authorized_request(self):
        factory = APIRequestFactory()
        view = APIDeleteUserRecipe.as_view()

        request = factory.post(
            reverse("api_delete_user_recipe", kwargs={"id": self.USER_RECIPE.external_id}),
            HTTP_X_API_KEY=self.API_KEY,
        )
        force_authenticate(request, user=self.USER)
        response = view(request, id=self.USER_RECIPE.external_id)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(0, user_recipe.load_lrecipes(self.USER).count())

    def test_delete_user_recipe_authorized_request_id_not_found(self):
        factory = APIRequestFactory()
        view = APIDeleteUserRecipe.as_view()

        request = factory.post(
            reverse("api_delete_user_recipe", kwargs={"id": test_constants.TEST_UUID_2}),
            HTTP_X_API_KEY=self.API_KEY,
        )
        force_authenticate(request, user=self.USER)
        response = view(request, id=test_constants.TEST_UUID_2)

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
