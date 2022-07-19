from __future__ import annotations

from http import HTTPStatus

from django.urls import reverse
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from nutrition_tracker.constants import constants
from nutrition_tracker.models import user_ingredient
from nutrition_tracker.rest_framework.views import APIEditUserIngredient
from nutrition_tracker.tests import objects as test_objects
from nutrition_tracker.utils import form as form_utils


class TestViewsAPIEditUserIngredient(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.API_KEY = test_objects.get_api_key()

    def test_unauthorized_get_fails(self):
        factory = APIRequestFactory()
        view = APIEditUserIngredient.as_view()

        request = factory.get(reverse("api_edit_user_ingredient"))
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_unauthorized_post_fails(self):
        factory = APIRequestFactory()
        view = APIEditUserIngredient.as_view()

        request = factory.post(reverse("api_edit_user_ingredient"))
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_authorized_get_no_api_key_fails(self):
        factory = APIRequestFactory()
        view = APIEditUserIngredient.as_view()

        request = factory.get(reverse("api_edit_user_ingredient"))
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_authorized_post_no_api_key_fails(self):
        factory = APIRequestFactory()
        view = APIEditUserIngredient.as_view()

        request = factory.post(reverse("api_edit_user_ingredient"))
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_edit_authorized_get_request(self):
        lfood = test_objects.get_user_ingredient()

        factory = APIRequestFactory()
        view = APIEditUserIngredient.as_view()

        request = factory.get(
            reverse("api_edit_user_ingredient", kwargs={"id": lfood.external_id}),
            HTTP_X_API_KEY=self.API_KEY,
        )
        force_authenticate(request, user=self.USER)
        response = view(request, id=lfood.external_id)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data["external_id"], str(lfood.external_id))
        self.assertEqual(response.data["name"], lfood.display_name)

    def test_edit_authorized_post_request(self):
        factory = APIRequestFactory()
        view = APIEditUserIngredient.as_view()
        nutrient_field_name = form_utils.get_field_name(constants.ENERGY_NUTRIENT_ID)

        request = factory.post(
            reverse("api_edit_user_ingredient"),
            {
                "name": "test",
                nutrient_field_name: constants.Threshold.MAX_VALUE,
                # Servings management form fields.
                "nutrition_tracker-userfoodportion-content_type-object_id-TOTAL_FORMS": "1",
                "nutrition_tracker-userfoodportion-content_type-object_id-INITIAL_FORMS": "0",
                "nutrition_tracker-userfoodportion-content_type-object_id-MIN_NUM_FORMS": "0",
                "nutrition_tracker-userfoodportion-content_type-object_id-MAX_NUM_FORMS": "1000",
            },
            HTTP_X_API_KEY=self.API_KEY,
        )
        force_authenticate(request, user=self.USER)
        response = view(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(user_ingredient.load_lfoods(self.USER).count(), 1)
