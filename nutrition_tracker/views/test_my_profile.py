from __future__ import annotations

import datetime
from http import HTTPStatus
from unittest.mock import patch

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from nutrition_tracker.biz import user
from nutrition_tracker.constants import constants
from nutrition_tracker.tests import constants as test_constants
from nutrition_tracker.tests import objects as test_objects


class TestViewsMyProfile(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()

    def test_logged_out_redirects(self):
        response = self.client.get(reverse("my_profile"), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/accounts/login/?next=/my_profile/")

    def test_logged_in_page_load_success(self):
        self.client.login(email="user@famnom.com", password="password")
        response = self.client.get(reverse("my_profile"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "nutrition_tracker/my_profile.html")

    def test_logged_in_save_success(self):
        self.client.login(email="user@famnom.com", password="password")
        new_date_of_birth = datetime.date(1953, 1, 4)
        response = self.client.post(
            reverse("my_profile"), {"date_of_birth": new_date_of_birth, "email": "user@famnom.com"}, follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, "/my_profile/")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(constants.MESSAGE_SUCCESS_PROFILE_SAVE, messages)
        self.USER.refresh_from_db()
        self.assertEqual(self.USER.date_of_birth, new_date_of_birth)

    def test_logged_in_save_family_id_raises(self):
        luser_2 = test_objects.get_user_2()
        user.add_to_family(luser_2, test_constants.TEST_UUID)
        self.client.login(email="user@famnom.com", password="password")
        new_date_of_birth = datetime.date(1953, 1, 4)
        response = self.client.post(
            reverse("my_profile"),
            {"date_of_birth": new_date_of_birth, "email": "user@famnom.com", "family_email": "user_2@famnom.com"},
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("user_2@famnom.com can not be added to your family.", messages)
        self.USER.refresh_from_db()
        self.assertNotEqual(self.USER.date_of_birth, new_date_of_birth)

    @patch("nutrition_tracker.constants.constants.MAX_FAMILY_SIZE", 1)
    def test_logged_in_save_family_id_max_family_raises(self):
        self.USER.family_id = test_constants.TEST_UUID
        self.USER.save()
        self.USER.refresh_from_db()
        test_objects.get_user_2()
        self.client.login(email="user@famnom.com", password="password")
        new_date_of_birth = datetime.date(1953, 1, 4)
        response = self.client.post(
            reverse("my_profile"),
            {"date_of_birth": new_date_of_birth, "email": "user@famnom.com", "family_email": "user_2@famnom.com"},
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("Can not add more than 1 members to a family.", messages)
        self.USER.refresh_from_db()
        self.assertNotEqual(self.USER.date_of_birth, new_date_of_birth)
