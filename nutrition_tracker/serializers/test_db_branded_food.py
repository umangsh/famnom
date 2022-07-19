from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.serializers import DBBrandedFoodSerializer
from nutrition_tracker.tests import objects as test_objects


class TestSerializersDBFood(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.DB_BRANDED_FOOD = test_objects.get_db_branded_food()
        cls.SERIALIZED_DB_BRANDED_FOOD = DBBrandedFoodSerializer(instance=cls.DB_BRANDED_FOOD)

    def test_contains_expected_fields(self):
        data = self.SERIALIZED_DB_BRANDED_FOOD.data
        self.assertEqual(
            set(data.keys()),
            {"brand_name", "subbrand_name", "brand_owner", "gtin_upc", "ingredients", "not_a_significant_source_of"},
        )

    def test_brand_name_content(self):
        data = self.SERIALIZED_DB_BRANDED_FOOD.data
        self.assertEqual(data["brand_name"], self.DB_BRANDED_FOOD.brand_name)

    def test_brand_owner_content(self):
        data = self.SERIALIZED_DB_BRANDED_FOOD.data
        self.assertEqual(data["brand_owner"], self.DB_BRANDED_FOOD.brand_owner)

    def test_gtin_upc_content(self):
        data = self.SERIALIZED_DB_BRANDED_FOOD.data
        self.assertEqual(data["gtin_upc"], self.DB_BRANDED_FOOD.gtin_upc)

    def test_ingredients_content(self):
        data = self.SERIALIZED_DB_BRANDED_FOOD.data
        self.assertIsNone(data["ingredients"])
