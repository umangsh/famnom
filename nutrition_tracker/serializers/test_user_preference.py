from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.serializers import UserPreferenceSerializer
from nutrition_tracker.tests import objects as test_objects


class TestSerializersUserPreference(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_PREFERENCE = test_objects.get_nutrient_preference()
        cls.SERIALIZED_USER_PREFERENCE = UserPreferenceSerializer(instance=cls.USER_PREFERENCE)

    def test_contains_expected_fields(self):
        data = self.SERIALIZED_USER_PREFERENCE.data
        self.assertEqual(set(data.keys()), {"food_nutrient_id", "thresholds"})

    def test_food_nutrient_id_content(self):
        data = self.SERIALIZED_USER_PREFERENCE.data
        self.assertEqual(data["food_nutrient_id"], self.USER_PREFERENCE.food_nutrient_id)

    def test_thresholds_content(self):
        data = self.SERIALIZED_USER_PREFERENCE.data
        self.assertEqual(len(data["thresholds"]), 1)
