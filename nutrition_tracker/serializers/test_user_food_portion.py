from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.serializers import UserFoodPortionSerializer
from nutrition_tracker.tests import objects as test_objects


class TestSerializersUserFoodPortion(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_FOOD_PORTION = test_objects.get_user_food_portion()
        cls.SERIALIZED_USER_FOOD_PORTION = UserFoodPortionSerializer(instance=cls.USER_FOOD_PORTION)

    def test_contains_expected_fields(self):
        data = self.SERIALIZED_USER_FOOD_PORTION.data
        self.assertEqual(
            set(data.keys()),
            {
                "id",
                "external_id",
                "servings_per_container",
                "household_quantity",
                "household_unit",
                "serving_size",
                "serving_size_unit",
            },
        )

    def test_id_content(self):
        data = self.SERIALIZED_USER_FOOD_PORTION.data
        self.assertEqual(data["id"], self.USER_FOOD_PORTION.id)

    def test_external_id_content(self):
        data = self.SERIALIZED_USER_FOOD_PORTION.data
        self.assertEqual(data["external_id"], str(self.USER_FOOD_PORTION.external_id))

    def test_servings_per_container_content(self):
        data = self.SERIALIZED_USER_FOOD_PORTION.data
        self.assertEqual(data["servings_per_container"], self.USER_FOOD_PORTION.servings_per_container)

    def test_household_quantity_content(self):
        data = self.SERIALIZED_USER_FOOD_PORTION.data
        self.assertIsNone(data["household_quantity"])

    def test_household_unit_content(self):
        data = self.SERIALIZED_USER_FOOD_PORTION.data
        self.assertIsNone(data["household_unit"])

    def test_serving_size_content(self):
        data = self.SERIALIZED_USER_FOOD_PORTION.data
        self.assertEqual(data["serving_size"], self.USER_FOOD_PORTION.serving_size)

    def test_serving_size_unit_content(self):
        data = self.SERIALIZED_USER_FOOD_PORTION.data
        self.assertEqual(data["serving_size_unit"], self.USER_FOOD_PORTION.serving_size_unit)
