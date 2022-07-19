from __future__ import annotations

from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from nutrition_tracker.tests import objects as test_objects


class TestViewsIndex(TestCase):
    def test_logged_out(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "nutrition_tracker/index.html")
        self.assertContains(response, "Welcome to Famnom!")
        self.assertContains(response, "Already have an account?")

    def test_logged_in_default_page(self):
        test_objects.get_user()
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "nutrition_tracker/index.html")
        self.assertContains(response, "Welcome <a")
        self.assertContains(response, "No meals added for today.")
        self.assertContains(response, "No nutrition goals found.")

    def test_logged_in_with_meals(self):
        test_objects.get_user()
        test_objects.get_meal_today_1()
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "nutrition_tracker/index.html")
        self.assertContains(response, "Welcome <a")
        self.assertContains(response, "Breakfast")
        self.assertContains(response, "No nutrition goals found.")

    def test_logged_in_with_tracker(self):
        test_objects.get_user()
        test_objects.get_nutrient_preference()
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "nutrition_tracker/index.html")
        self.assertContains(response, "Welcome <a")
        self.assertContains(response, "No meals added for today.")
        self.assertContains(response, "Tracker")

    def test_logged_in_with_meals_and_tracker(self):
        test_objects.get_user()
        test_objects.get_meal_today_1()
        test_objects.get_nutrient_preference()
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "nutrition_tracker/index.html")
        self.assertContains(response, "Welcome <a")
        self.assertContains(response, "Breakfast")
        self.assertContains(response, "Tracker")
