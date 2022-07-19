from __future__ import annotations

from http import HTTPStatus

from django.urls import reverse
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from nutrition_tracker.models import user_food_membership, user_food_portion, user_meal
from nutrition_tracker.rest_framework.views import APIEditUserMeal
from nutrition_tracker.tests import objects as test_objects


class TestViewsAPIEditUserMeal(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.API_KEY = test_objects.get_api_key()

    def test_unauthorized_get_fails(self):
        factory = APIRequestFactory()
        view = APIEditUserMeal.as_view()

        request = factory.get(reverse("api_edit_user_meal"))
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_unauthorized_post_fails(self):
        factory = APIRequestFactory()
        view = APIEditUserMeal.as_view()

        request = factory.post(reverse("api_edit_user_meal"))
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_authorized_get_no_api_key_fails(self):
        factory = APIRequestFactory()
        view = APIEditUserMeal.as_view()

        request = factory.get(reverse("api_edit_user_meal"))
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_authorized_post_no_api_key_fails(self):
        factory = APIRequestFactory()
        view = APIEditUserMeal.as_view()

        request = factory.post(reverse("api_edit_user_meal"))
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_edit_authorized_get_request(self):
        lmeal = test_objects.get_meal_today_1()

        factory = APIRequestFactory()
        view = APIEditUserMeal.as_view()

        request = factory.get(
            reverse("api_edit_user_meal", kwargs={"id": lmeal.external_id}),
            HTTP_X_API_KEY=self.API_KEY,
        )
        force_authenticate(request, user=self.USER)
        response = view(request, id=lmeal.external_id)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data["external_id"], str(lmeal.external_id))
        self.assertEqual(response.data["meal_type"], lmeal.meal_type)

    def test_edit_authorized_post_request(self):
        factory = APIRequestFactory()
        view = APIEditUserMeal.as_view()

        lfood = test_objects.get_user_ingredient()

        request = factory.post(
            reverse("api_edit_user_meal"),
            {
                "meal_type": "Lunch",
                "meal_date": "2022-04-03",
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
            },
            HTTP_X_API_KEY=self.API_KEY,
        )
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(user_meal.load_lmeals(self.USER).count(), 1)
        self.assertEqual(user_food_portion.load_lfood_portions(self.USER).count(), 1)
        self.assertEqual(user_food_membership.load_lmemberships(self.USER).count(), 1)
