from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.serializers import UserDataSerializer
from nutrition_tracker.tests import constants as test_constants
from nutrition_tracker.tests import objects as test_objects


class TestSerializersUser(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.SERIALIZED_USER = UserDataSerializer(instance=cls.USER)

    def test_contains_expected_fields(self):
        data = self.SERIALIZED_USER.data
        self.assertEqual(
            set(data.keys()),
            {
                "external_id",
                "first_name",
                "last_name",
                "email",
                "date_of_birth",
                "is_pregnant",
                "family_members",
            },
        )

    def test_external_id_content(self):
        data = self.SERIALIZED_USER.data
        self.assertEqual(data["external_id"], str(self.USER.external_id))

    def test_first_name_content(self):
        data = self.SERIALIZED_USER.data
        self.assertEqual(data["first_name"], "Test")

    def test_last_name_content(self):
        data = self.SERIALIZED_USER.data
        self.assertEqual(data["last_name"], "Gupta")

    def test_email_content(self):
        data = self.SERIALIZED_USER.data
        self.assertEqual(data["email"], "user@famnom.com")

    def test_is_pregnant_content(self):
        data = self.SERIALIZED_USER.data
        self.assertFalse(data["is_pregnant"])

    def test_family_members_content(self):
        self.USER.family_id = test_constants.TEST_UUID
        self.USER.save()
        self.USER.refresh_from_db()

        luser_2 = test_objects.get_user_2()
        luser_2.family_id = test_constants.TEST_UUID
        luser_2.save()
        luser_2.refresh_from_db()

        self.SERIALIZED_USER = UserDataSerializer(instance=self.USER)
        data = self.SERIALIZED_USER.data
        self.assertCountEqual(data["family_members"], ["user@famnom.com", "user_2@famnom.com"])

    def test_update(self):
        data = {"first_name": "Changed", "email": "user@famnom.com", "is_pregnant": True}
        self.SERIALIZED_USER = UserDataSerializer(instance=self.USER, data=data)
        self.assertTrue(self.SERIALIZED_USER.is_valid())

        self.SERIALIZED_USER.update(self.USER, self.SERIALIZED_USER.validated_data)
        self.USER.refresh_from_db()
        self.assertEqual(self.USER.first_name, "Changed")
        self.assertTrue(self.USER.is_pregnant())
