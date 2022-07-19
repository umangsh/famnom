from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import food_portion
from nutrition_tracker.serializers import LogSerializer
from nutrition_tracker.tests import objects as test_objects


class TestSerializersLogSerializer(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.DB_FOOD = test_objects.get_db_food()

    def test_log_dbfood_init(self):
        serializer = LogSerializer(
            data={
                "external_id": self.DB_FOOD.external_id,
            },
            context={
                "user": self.USER,
                "external_id": self.DB_FOOD.external_id,
                "cfood": self.DB_FOOD,
                "food_portions": food_portion.for_display_choices(None, self.DB_FOOD),
            },
        )
        self.assertTrue(serializer.is_valid())

    def test_log_dbfood_to_meal(self):
        db_food_portion = test_objects.get_db_food_portion()
        serializer = LogSerializer(
            data={
                "external_id": self.DB_FOOD.external_id,
                "meal_type": constants.MealType.DINNER,
                "meal_date": "2020-05-05",
                "quantity": 4,
                "serving": f"{db_food_portion.external_id}",
            },
            context={
                "user": self.USER,
                "external_id": self.DB_FOOD.external_id,
                "cfood": self.DB_FOOD,
                "food_portions": food_portion.for_display_choices(None, self.DB_FOOD),
            },
        )
        self.assertTrue(serializer.is_valid())
