from __future__ import annotations

from http import HTTPStatus

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from nutrition_tracker.constants import constants
from nutrition_tracker.tests import objects as test_objects


class TestViewsNutrient(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()

    def test_nutrient_id_invalid(self):
        response = self.client.get(reverse("nutrient", kwargs={"id": 1}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_ERROR_NUTRIENT_NOT_FOUND, messages)

    def test_nutrient_logged_out(self):
        response = self.client.get(reverse("nutrient", kwargs={"id": constants.ENERGY_NUTRIENT_ID}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "nutrition_tracker/nutrient.html")
        self.assertTrue(response.context["lnutrient"])
        self.assertContains(response, "Calories")
        self.assertContains(response, "Read More")
        self.assertContains(response, "From Food Database")

    def test_nutrient_logged_in(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("nutrient", kwargs={"id": constants.ENERGY_NUTRIENT_ID}), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "nutrition_tracker/nutrient.html")
        self.assertTrue(response.context["lnutrient"])
        self.assertContains(response, "Calories")
        self.assertContains(response, "Read More")
        self.assertContains(response, "In Recent Meals")
        self.assertContains(response, "From MyKitchen")
        self.assertContains(response, "From Food Database")
