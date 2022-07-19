from __future__ import annotations

from http import HTTPStatus

from django.urls import reverse
from rest_framework.renderers import JSONRenderer
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from nutrition_tracker.logic import user_prefs
from nutrition_tracker.models import user_meal
from nutrition_tracker.rest_framework.views import APIMealplanFormOne, APIMealplanFormThree, APIMealplanFormTwo
from nutrition_tracker.tests import objects as test_objects
from nutrition_tracker.utils import form as form_utils


class TestViewsAPIMealplanFormOne(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.API_KEY = test_objects.get_api_key()

    def test_unauthorized_get_fails(self):
        factory = APIRequestFactory()
        view = APIMealplanFormOne.as_view()

        request = factory.get(reverse("api_mealplan_form_one"))
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_unauthorized_post_fails(self):
        factory = APIRequestFactory()
        view = APIMealplanFormOne.as_view()

        request = factory.post(reverse("api_mealplan_form_one"))
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_authorized_get_no_api_key_fails(self):
        factory = APIRequestFactory()
        view = APIMealplanFormOne.as_view()

        request = factory.get(reverse("api_mealplan_form_one"))
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_authorized_post_no_api_key_fails(self):
        factory = APIRequestFactory()
        view = APIMealplanFormOne.as_view()

        request = factory.post(reverse("api_mealplan_form_one"))
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_authorized_post_request(self):
        lfood = test_objects.get_user_ingredient()
        lfood_2 = test_objects.get_user_ingredient_2()
        factory = APIRequestFactory()
        view = APIMealplanFormOne.as_view()

        request = factory.post(
            reverse("api_mealplan_form_one"),
            {
                "available_foods": [lfood.external_id],
                "must_have_foods": [lfood_2.external_id],
            },
            HTTP_X_API_KEY=self.API_KEY,
        )
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(user_prefs.load_food_preferences(self.USER).count(), 2)


class TestViewsAPIMealplanFormTwo(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.API_KEY = test_objects.get_api_key()

    def test_unauthorized_get_fails(self):
        factory = APIRequestFactory()
        view = APIMealplanFormTwo.as_view()

        request = factory.get(reverse("api_mealplan_form_two"))
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_unauthorized_post_fails(self):
        factory = APIRequestFactory()
        view = APIMealplanFormTwo.as_view()

        request = factory.post(reverse("api_mealplan_form_two"))
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_authorized_get_no_api_key_fails(self):
        factory = APIRequestFactory()
        view = APIMealplanFormTwo.as_view()

        request = factory.get(reverse("api_mealplan_form_two"))
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_authorized_post_no_api_key_fails(self):
        factory = APIRequestFactory()
        view = APIMealplanFormTwo.as_view()

        request = factory.post(reverse("api_mealplan_form_two"))
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_authorized_post_request(self):
        lfood = test_objects.get_user_ingredient()
        field_name = form_utils.get_field_name(lfood.external_id)
        threshold_field_name = form_utils.get_threshold_field_name(lfood.external_id)

        factory = APIRequestFactory()
        view = APIMealplanFormTwo.as_view()

        request = factory.post(
            reverse("api_mealplan_form_two"),
            {
                field_name: 5,
                threshold_field_name: "2",
            },
            HTTP_X_API_KEY=self.API_KEY,
        )
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(user_prefs.load_food_preferences(self.USER).count(), 1)

    def test_authorized_get_request(self):
        lfood = test_objects.get_user_ingredient()
        test_objects.get_user_preference()
        lrecipe = test_objects.get_recipe()
        test_objects.get_user_recipe_preference()

        factory = APIRequestFactory()
        view = APIMealplanFormTwo.as_view()

        request = factory.get(
            reverse("api_mealplan_form_two"),
            HTTP_X_API_KEY=self.API_KEY,
        )
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertJSONEqual(
            JSONRenderer().render(response.data),
            [
                {
                    "external_id": str(lfood.external_id),
                    "name": "test",
                    "thresholds": [{"min_value": 5.0, "max_value": None, "exact_value": None}],
                },
                {
                    "external_id": str(lrecipe.external_id),
                    "name": "Test Recipe",
                    "thresholds": [{"min_value": 5.0, "max_value": None, "exact_value": None}],
                },
            ],
        )


class TestViewsAPIMealplanFormThree(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.USER_INGREDIENT = test_objects.get_user_ingredient()
        test_objects.get_user_food_nutrient()
        test_objects.get_user_food_portion()
        cls.USER_INGREDIENT_2 = test_objects.get_user_ingredient_2()
        test_objects.get_user_2_food_nutrient()
        test_objects.get_user_2_food_portion()
        test_objects.get_nutrient_preference()
        cls.API_KEY = test_objects.get_api_key()

    def test_unauthorized_get_fails(self):
        factory = APIRequestFactory()
        view = APIMealplanFormThree.as_view()

        request = factory.get(reverse("api_mealplan_form_three"))
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_unauthorized_post_fails(self):
        factory = APIRequestFactory()
        view = APIMealplanFormThree.as_view()

        request = factory.post(reverse("api_mealplan_form_three"))
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_authorized_get_no_api_key_fails(self):
        factory = APIRequestFactory()
        view = APIMealplanFormTwo.as_view()

        request = factory.get(reverse("api_mealplan_form_two"))
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_authorized_post_no_api_key_fails(self):
        factory = APIRequestFactory()
        view = APIMealplanFormThree.as_view()

        request = factory.post(reverse("api_mealplan_form_three"))
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_authorized_post_request(self):
        lfood = test_objects.get_user_ingredient()
        field_name = form_utils.get_field_name(lfood.external_id)
        meal_field_name = form_utils.get_meal_field_name(lfood.external_id)

        factory = APIRequestFactory()
        view = APIMealplanFormThree.as_view()

        request = factory.post(
            reverse("api_mealplan_form_three"),
            {
                field_name: 5,
                meal_field_name: "Lunch",
            },
            HTTP_X_API_KEY=self.API_KEY,
        )
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(user_meal.load_lmeals(self.USER).count(), 1)

    def test_authorized_get_request(self):
        factory = APIRequestFactory()
        view = APIMealplanFormThree.as_view()

        request = factory.get(
            reverse("api_mealplan_form_three"),
            HTTP_X_API_KEY=self.API_KEY,
        )
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(response.data["infeasible"])
        self.assertEqual(len(response.data["results"]), 1)
