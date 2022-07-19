from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.constants import constants
from nutrition_tracker.models import user_ingredient
from nutrition_tracker.serializers import FoodFormSerializer
from nutrition_tracker.tests import objects as test_objects
from nutrition_tracker.utils import form as form_utils


class TestSerializersFoodForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        lfood = test_objects.get_user_ingredient()
        cls.LFOOD = user_ingredient.load_lfood(cls.USER, external_id=lfood.external_id)

    def test_init_no_energy_throws(self):
        serializer = FoodFormSerializer(
            data={},
            context={
                "user": self.USER,
            },
        )
        self.assertFalse(serializer.is_valid())

    def test_init(self):
        nutrient_field_name = form_utils.get_field_name(constants.ENERGY_NUTRIENT_ID)
        serializer = FoodFormSerializer(
            data={
                nutrient_field_name: 100,
            },
            context={
                "user": self.USER,
            },
        )
        self.assertTrue(serializer.is_valid())

    def test_values_validation_fail_throws(self):
        nutrient_field_name = form_utils.get_field_name(constants.ENERGY_NUTRIENT_ID)
        serializer = FoodFormSerializer(
            data={
                "name": "Test",
                nutrient_field_name: "abc",
            },
            context={
                "user": self.USER,
            },
        )
        self.assertFalse(serializer.is_valid())

    def test_values(self):
        nutrient_field_name = form_utils.get_field_name(constants.ENERGY_NUTRIENT_ID)
        serializer = FoodFormSerializer(
            data={
                "name": "Test",
                nutrient_field_name: 100,
            },
            context={
                "user": self.USER,
                "lfood": self.LFOOD,
            },
        )
        self.assertTrue(serializer.is_valid())
