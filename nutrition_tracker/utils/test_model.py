from __future__ import annotations

import dataclasses
from typing import ClassVar

from django.test import SimpleTestCase, TestCase

from nutrition_tracker.models import user_meal
from nutrition_tracker.tests import objects as test_objects
from nutrition_tracker.utils import model


@dataclasses.dataclass
class FakeField:
    def __init__(self, name: str):
        self.name: str = name


class TestUtilsModelGetFieldNames(SimpleTestCase):
    def setUp(self) -> None:
        self.field_alpha: FakeField = FakeField(name="alpha")
        self.field_beta: FakeField = FakeField(name="beta")
        self.field_name: FakeField = FakeField(name="name")
        self.field_id: FakeField = FakeField(name="id")
        self.field_list: list[FakeField] = [self.field_alpha, self.field_beta, self.field_name, self.field_id]

    def test_get_field_names_for_display_with_defaults(self) -> None:
        expected_field_list: list[str] = [self.field_alpha.name, self.field_beta.name, self.field_name.name]
        self.assertEqual(expected_field_list, model.get_field_names(self.field_list))

    def test_get_field_names_for_display_skip_fields_empty(self) -> None:
        expected_field_list: list[str] = [
            self.field_alpha.name,
            self.field_beta.name,
            self.field_name.name,
            self.field_id.name,
        ]
        self.assertEqual(expected_field_list, model.get_field_names(self.field_list, skip_fields=[]))

    def test_get_field_names_for_display_prefix_fields_non_empty(self) -> None:
        expected_field_list: list[str] = [self.field_name.name, self.field_beta.name, self.field_alpha.name]
        self.assertEqual(
            expected_field_list,
            model.get_field_names(
                self.field_list, prefix_fields_in_order=[self.field_name.name, self.field_beta.name]
            ),
        )

    def test_get_field_names_for_display_prefix_fields_non_empty_skip_fields_empty(self) -> None:
        expected_field_list: list[str] = [
            self.field_name.name,
            self.field_beta.name,
            self.field_alpha.name,
            self.field_id.name,
        ]
        self.assertEqual(
            expected_field_list,
            model.get_field_names(
                self.field_list, prefix_fields_in_order=[self.field_name.name, self.field_beta.name], skip_fields=[]
            ),
        )


class TestUtilsModelSortMeals(TestCase):
    USER_MEAL_TODAY_1: ClassVar[user_meal.UserMeal]
    USER_MEAL_TODAY_2: ClassVar[user_meal.UserMeal]
    USER_MEAL_YESTERDAY_1: ClassVar[user_meal.UserMeal]
    USER_MEAL_YESTERDAY_2: ClassVar[user_meal.UserMeal]

    @classmethod
    def setUpTestData(cls) -> None:
        cls.USER_MEAL_TODAY_1 = test_objects.get_meal_today_1()
        cls.USER_MEAL_TODAY_2 = test_objects.get_meal_today_2()
        cls.USER_MEAL_YESTERDAY_1 = test_objects.get_meal_yesterday_1()
        cls.USER_MEAL_YESTERDAY_2 = test_objects.get_meal_yesterday_2()

    def test_sort_meals(self) -> None:
        lmeals: list[user_meal.UserMeal] = [
            self.USER_MEAL_YESTERDAY_2,
            self.USER_MEAL_YESTERDAY_1,
            self.USER_MEAL_TODAY_2,
            self.USER_MEAL_TODAY_1,
        ]
        expected_output: list[user_meal.UserMeal] = [
            self.USER_MEAL_YESTERDAY_1,
            self.USER_MEAL_YESTERDAY_2,
            self.USER_MEAL_TODAY_1,
            self.USER_MEAL_TODAY_2,
        ]
        self.assertEqual(expected_output, model.sort_meals(lmeals))

    def test_sort_meals_reverse(self) -> None:
        lmeals: list[user_meal.UserMeal] = [
            self.USER_MEAL_YESTERDAY_2,
            self.USER_MEAL_YESTERDAY_1,
            self.USER_MEAL_TODAY_2,
            self.USER_MEAL_TODAY_1,
        ]
        expected_output: list[user_meal.UserMeal] = [
            self.USER_MEAL_TODAY_2,
            self.USER_MEAL_TODAY_1,
            self.USER_MEAL_YESTERDAY_2,
            self.USER_MEAL_YESTERDAY_1,
        ]
        self.assertEqual(expected_output, model.sort_meals(lmeals, reverse=True))
