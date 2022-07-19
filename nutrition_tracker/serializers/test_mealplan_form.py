from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.serializers import (
    MealplanFormOneSerializer,
    MealplanFormThreeSerializer,
    MealplanFormTwoSerializer,
)
from nutrition_tracker.tests import constants as test_constants
from nutrition_tracker.tests import objects as test_objects
from nutrition_tracker.utils import form as form_utils


class TestSerializersMealplanFormOne(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()

    def test_init(self):
        serializer = MealplanFormOneSerializer(
            data={},
            context={
                "user": self.USER,
            },
        )
        self.assertTrue(serializer.is_valid())

    def test_with_values(self):
        serializer = MealplanFormOneSerializer(
            data={
                "available_foods": [test_constants.TEST_UUID, test_constants.TEST_UUID_2],
                "must_have_recipes": [test_constants.TEST_UUID, test_constants.TEST_UUID_2],
            },
            context={
                "user": self.USER,
            },
        )
        self.assertTrue(serializer.is_valid())

    def test_error_values_invalid(self):
        serializer = MealplanFormOneSerializer(
            data={
                "available_foods": [test_constants.TEST_UUID, "not_a_uuid"],
            },
            context={
                "user": self.USER,
            },
        )
        self.assertFalse(serializer.is_valid())


class TestSerializersMealplanFormTwo(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()

    def test_init(self):
        serializer = MealplanFormTwoSerializer(
            data={},
            context={
                "user": self.USER,
            },
        )
        self.assertTrue(serializer.is_valid())

    def test_with_values(self):
        field_name = form_utils.get_field_name(test_constants.TEST_UUID)
        threshold_field_name = form_utils.get_threshold_field_name(test_constants.TEST_UUID)

        serializer = MealplanFormTwoSerializer(
            data={
                field_name: 5,
                threshold_field_name: "2",
            },
            context={
                "user": self.USER,
            },
        )
        self.assertTrue(serializer.is_valid())


class TestSerializersMealplanFormThree(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()

    def test_init(self):
        serializer = MealplanFormThreeSerializer(
            data={},
            context={
                "user": self.USER,
            },
        )
        self.assertTrue(serializer.is_valid())

    def test_with_values(self):
        field_name = form_utils.get_field_name(test_constants.TEST_UUID)
        meal_field_name = form_utils.get_meal_field_name(test_constants.TEST_UUID)

        serializer = MealplanFormThreeSerializer(
            data={
                field_name: 5,
                meal_field_name: "Lunch",
            },
            context={
                "user": self.USER,
            },
        )
        self.assertTrue(serializer.is_valid())
