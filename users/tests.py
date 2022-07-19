# pylint: skip-file
"""User tests."""
from __future__ import annotations

from allauth.account import signals
from allauth.account.models import EmailAddress
from django.test import TestCase

import users.models as user_model
from nutrition_tracker.tests import objects as test_objects


class UserManagerTestCase(TestCase):
    def test_create_user(self):
        user = user_model.User.objects.create_user("random@gmail.com", "password123")
        self.assertTrue(isinstance(user, user_model.User))

    def test_create_superuser(self):
        user = user_model.User.objects.create_superuser("random@gmail.com", "password123")
        self.assertTrue(isinstance(user, user_model.User))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)


class TestModelsUser(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()

    def test_generated_fields(self):
        self.assertTrue(self.USER.date_of_birth)
        self.assertTrue(self.USER.external_id)
        self.assertFalse(self.USER.is_staff)
        self.assertTrue(self.USER.is_active)
        self.assertFalse(self.USER.is_superuser)

    def test_add_email(self):
        test_objects.verify_user(self.USER)
        self.USER.add_email("new_email@address.com")
        self.assertEqual(2, EmailAddress.objects.filter(user=self.USER).count())

    def test_update_user_email(self):
        test_objects.verify_user(self.USER)
        new_email = "new_email@address.com"
        self.USER.add_email(new_email)
        self.assertEqual(2, EmailAddress.objects.filter(user=self.USER).count())

        email_address = EmailAddress.objects.get(email=new_email)
        signals.email_confirmed.send(sender=self.__class__, request=None, email_address=email_address)
        self.assertEqual(1, EmailAddress.objects.filter(user=self.USER).count())

    def test_get_flag(self):
        self.assertFalse(self.USER.get_flag(user_model.User.FLAG_IS_PREGNANT))

    def test_add_flag(self):
        self.assertFalse(self.USER.is_pregnant())
        self.USER.add_flag(user_model.User.FLAG_IS_PREGNANT)
        self.assertTrue(self.USER.is_pregnant())

    def test_remove_flag(self):
        self.USER.add_flag(user_model.User.FLAG_IS_PREGNANT)
        self.assertTrue(self.USER.is_pregnant())
        self.USER.remove_flag(user_model.User.FLAG_IS_PREGNANT)
        self.assertFalse(self.USER.is_pregnant())

    def test_update_flag(self):
        self.assertFalse(self.USER.is_pregnant())
        self.USER.update_flag(user_model.User.FLAG_IS_PREGNANT, True)
        self.assertTrue(self.USER.is_pregnant())
        self.USER.update_flag(user_model.User.FLAG_IS_PREGNANT, False)
        self.assertFalse(self.USER.is_pregnant())

    def test_get_full_name(self):
        self.assertEqual(self.USER.get_full_name(), "Test Gupta")

    def test_get_short_name(self):
        self.assertEqual(self.USER.get_short_name(), "Test")

    def test_string_representation(self):
        self.assertEqual(str(self.USER), "Test")
        luser_2 = test_objects.get_user_2()
        self.assertEqual(str(luser_2), "user_2@famnom.com")
