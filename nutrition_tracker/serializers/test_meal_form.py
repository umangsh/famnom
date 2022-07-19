from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.models import user_meal
from nutrition_tracker.serializers import MealFormSerializer
from nutrition_tracker.tests import objects as test_objects


class TestSerializersMealForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        lmeal = test_objects.get_meal_today_1()
        cls.LMEAL = user_meal.load_lmeal(cls.USER, external_id=lmeal.external_id)

    def test_init_name_missing_error(self):
        serializer = MealFormSerializer(
            data={},
            context={
                "user": self.USER,
            },
        )
        self.assertFalse(serializer.is_valid())

    def test_init(self):
        serializer = MealFormSerializer(
            data={
                "meal_type": self.LMEAL.meal_type,
                "meal_date": self.LMEAL.meal_date,
            },
            context={
                "user": self.USER,
            },
        )
        self.assertTrue(serializer.is_valid())

    def test_values_with_existing_meal(self):
        serializer = MealFormSerializer(
            data={
                "meal_type": self.LMEAL.meal_type,
                "meal_date": self.LMEAL.meal_date,
            },
            context={
                "user": self.USER,
                "lmeal": self.LMEAL,
            },
        )
        self.assertTrue(serializer.is_valid())
