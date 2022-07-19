from __future__ import annotations

from http import HTTPStatus

from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from nutrition_tracker.constants import constants
from nutrition_tracker.models import user_ingredient, user_meal
from nutrition_tracker.rest_framework.views import APILogDBFood
from nutrition_tracker.tests import constants as test_constants
from nutrition_tracker.tests import objects as test_objects


class TestViewsAPILogDBFood(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.DB_FOOD = test_objects.get_db_food()
        cls.USER = test_objects.get_user()
        cls.API_KEY = test_objects.get_api_key()

    def test_unauthorized_post_fails(self):
        factory = APIRequestFactory()
        view = APILogDBFood.as_view()

        request = factory.post(reverse("api_log_db_food", kwargs={"id": self.DB_FOOD.external_id}))
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_authorized_post_no_api_key_fails(self):
        factory = APIRequestFactory()
        view = APILogDBFood.as_view()

        request = factory.post(reverse("api_log_db_food", kwargs={"id": self.DB_FOOD.external_id}))
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_log_authorized_request(self):
        factory = APIRequestFactory()
        view = APILogDBFood.as_view()

        request = factory.post(
            reverse("api_log_db_food", kwargs={"id": self.DB_FOOD.external_id}),
            {"external_id": self.DB_FOOD.external_id, "meal_type": constants.MealType.LUNCH},
            HTTP_X_API_KEY=self.API_KEY,
        )
        force_authenticate(request, user=self.USER)
        response = view(request, id=self.DB_FOOD.external_id)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_log_authorized_request_bad_meal_type(self):
        factory = APIRequestFactory()
        view = APILogDBFood.as_view()

        request = factory.post(
            reverse("api_log_db_food", kwargs={"id": self.DB_FOOD.external_id}),
            {"external_id": self.DB_FOOD.external_id, "meal_type": constants.MealType.__empty__},
            HTTP_X_API_KEY=self.API_KEY,
        )
        force_authenticate(request, user=self.USER)
        response = view(request, id=self.DB_FOOD.external_id)

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_log_authorized_mutation_request(self):
        factory = APIRequestFactory()
        view = APILogDBFood.as_view()

        request = factory.post(
            reverse("api_log_db_food", kwargs={"id": self.DB_FOOD.external_id}),
            {
                "external_id": self.DB_FOOD.external_id,
                "meal_type": constants.MealType.LUNCH,
                "meal_date": timezone.localdate(),
                "serving": f"{constants.HUNDRED_SERVING_ID}",
                "quantity": 2,
            },
            HTTP_X_API_KEY=self.API_KEY,
        )
        force_authenticate(request, user=self.USER)
        response = view(request, id=self.DB_FOOD.external_id)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(user_meal.load_lmeals(self.USER).count(), 1)
        self.assertEqual(user_ingredient.load_lfoods(self.USER).count(), 1)

    def test_log_authorized_mutation_existing_lfood_request(self):
        test_objects.get_user_ingredient()
        self.assertEqual(user_ingredient.load_lfoods(self.USER).count(), 1)

        factory = APIRequestFactory()
        view = APILogDBFood.as_view()

        request = factory.post(
            reverse("api_log_db_food", kwargs={"id": self.DB_FOOD.external_id}),
            {
                "external_id": self.DB_FOOD.external_id,
                "meal_type": constants.MealType.LUNCH,
                "meal_date": timezone.localdate(),
                "serving": f"{constants.HUNDRED_SERVING_ID}",
                "quantity": 2,
            },
            HTTP_X_API_KEY=self.API_KEY,
        )
        force_authenticate(request, user=self.USER)
        response = view(request, id=self.DB_FOOD.external_id)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(user_meal.load_lmeals(self.USER).count(), 1)
        self.assertEqual(user_ingredient.load_lfoods(self.USER).count(), 1)

    def test_log_authorized_request_bad_id(self):
        factory = APIRequestFactory()
        view = APILogDBFood.as_view()

        request = factory.post(
            reverse("api_log_db_food", kwargs={"id": self.DB_FOOD.external_id}),
            {"external_id": "badid"},
            HTTP_X_API_KEY=self.API_KEY,
        )
        force_authenticate(request, user=self.USER)
        response = view(request, id=self.DB_FOOD.external_id)

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_log_authorized_request_no_id(self):
        factory = APIRequestFactory()
        view = APILogDBFood.as_view()

        request = factory.post(
            reverse("api_log_db_food", kwargs={"id": self.DB_FOOD.external_id}), {}, HTTP_X_API_KEY=self.API_KEY
        )
        force_authenticate(request, user=self.USER)
        response = view(request, id=self.DB_FOOD.external_id)

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_log_authorized_request_id_not_found(self):
        factory = APIRequestFactory()
        view = APILogDBFood.as_view()

        request = factory.post(
            reverse("api_log_db_food", kwargs={"id": test_constants.TEST_UUID_2}), {}, HTTP_X_API_KEY=self.API_KEY
        )
        force_authenticate(request, user=self.USER)
        response = view(request, id=test_constants.TEST_UUID_2)

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
