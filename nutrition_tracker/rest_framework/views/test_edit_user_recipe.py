from __future__ import annotations

from http import HTTPStatus

from django.urls import reverse
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from nutrition_tracker.constants import constants
from nutrition_tracker.models import user_food_membership, user_food_portion, user_recipe
from nutrition_tracker.rest_framework.views import APIEditUserRecipe
from nutrition_tracker.tests import objects as test_objects


class TestViewsAPIEditUserRecipe(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.API_KEY = test_objects.get_api_key()

    def test_unauthorized_get_fails(self):
        factory = APIRequestFactory()
        view = APIEditUserRecipe.as_view()

        request = factory.get(reverse("api_edit_user_recipe"))
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_unauthorized_post_fails(self):
        factory = APIRequestFactory()
        view = APIEditUserRecipe.as_view()

        request = factory.post(reverse("api_edit_user_recipe"))
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_authorized_get_no_api_key_fails(self):
        factory = APIRequestFactory()
        view = APIEditUserRecipe.as_view()

        request = factory.get(reverse("api_edit_user_recipe"))
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_authorized_post_no_api_key_fails(self):
        factory = APIRequestFactory()
        view = APIEditUserRecipe.as_view()

        request = factory.post(reverse("api_edit_user_recipe"))
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_edit_authorized_get_request(self):
        lrecipe = test_objects.get_recipe()

        factory = APIRequestFactory()
        view = APIEditUserRecipe.as_view()

        request = factory.get(
            reverse("api_edit_user_recipe", kwargs={"id": lrecipe.external_id}),
            HTTP_X_API_KEY=self.API_KEY,
        )
        force_authenticate(request, user=self.USER)
        response = view(request, id=lrecipe.external_id)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data["external_id"], str(lrecipe.external_id))
        self.assertEqual(response.data["name"], lrecipe.name)

    def test_edit_authorized_post_request(self):
        factory = APIRequestFactory()
        view = APIEditUserRecipe.as_view()

        lfood = test_objects.get_user_ingredient()

        request = factory.post(
            reverse("api_edit_user_recipe"),
            {
                "name": "test",
                # Foods management form fields.
                "food-TOTAL_FORMS": "1",
                "food-INITIAL_FORMS": "0",
                "food-MIN_NUM_FORMS": "0",
                "food-MAX_NUM_FORMS": "1000",
                # Food (new)
                "food-0-child_external_id": lfood.external_id,
                "food-0-quantity": 3,
                "food-0-serving": -3,
                # Recipes management form data
                "recipe-TOTAL_FORMS": "0",
                "recipe-INITIAL_FORMS": "0",
                "recipe-MIN_NUM_FORMS": "0",
                "recipe-MAX_NUM_FORMS": "1000",
                # Servings management form data
                "servings-TOTAL_FORMS": "2",
                "servings-INITIAL_FORMS": "0",
                "servings-MIN_NUM_FORMS": "0",
                "servings-MAX_NUM_FORMS": "1000",
                # First serving (new)
                "servings-0-serving_size": 200,
                "servings-0-serving_size_unit": constants.ServingSizeUnit.WEIGHT,
                # Second serving (new)
                "servings-1-serving_size": 150,
                "servings-1-serving_size_unit": constants.ServingSizeUnit.WEIGHT,
                "servings-1-household_quantity": "1/8",
                "servings-1-measure_unit": 1000,
            },
            HTTP_X_API_KEY=self.API_KEY,
        )
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(user_recipe.load_lrecipes(self.USER).count(), 1)
        self.assertEqual(user_food_portion.load_lfood_portions(self.USER).count(), 3)
        self.assertEqual(user_food_membership.load_lmemberships(self.USER).count(), 1)
