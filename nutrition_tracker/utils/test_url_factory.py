from __future__ import annotations

from typing import Any

from django.test import SimpleTestCase

from nutrition_tracker.tests import constants as test_constants
from nutrition_tracker.utils import url_factory


class TestUtilsUrlFactoryGetUrl(SimpleTestCase):
    def test_get_url_empty_kwargs(self) -> None:
        path: str = "/abc/"
        kwargs: dict[str, Any] = {}
        expected_output: str = "/abc/"
        self.assertEqual(expected_output, url_factory.get_url(path, **kwargs))

    def test_get_url(self) -> None:
        path: str = "/abc/"
        kwargs: dict[str, Any] = {"a": "1", "b": 2}
        expected_output: str = "/abc/?a=1&b=2"
        self.assertEqual(expected_output, url_factory.get_url(path, **kwargs))


class TestUtilsUrlFactoryGetIngredientUrl(SimpleTestCase):
    def test_get_ingredient_url(self) -> None:
        external_id: str = test_constants.TEST_UUID
        kwargs: dict[str, Any] = {"abc": "123"}
        expected_output: str = "/my_ingredient/" + test_constants.TEST_UUID + "/?abc=123"
        self.assertEqual(expected_output, url_factory.get_ingredient_url(external_id, **kwargs))


class TestUtilsUrlFactoryGetFoodUrl(SimpleTestCase):
    def test_get_food_url(self) -> None:
        external_id: str = test_constants.TEST_UUID
        kwargs: dict[str, Any] = {"abc": "123"}
        expected_output: str = "/my_food/" + test_constants.TEST_UUID + "/?abc=123"
        self.assertEqual(expected_output, url_factory.get_food_url(external_id, **kwargs))
