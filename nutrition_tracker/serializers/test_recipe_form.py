from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.models import user_recipe
from nutrition_tracker.serializers import RecipeFormSerializer
from nutrition_tracker.tests import objects as test_objects


class TestSerializersRecipeForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        lrecipe = test_objects.get_recipe()
        cls.LRECIPE = user_recipe.load_lrecipe(cls.USER, external_id=lrecipe.external_id)

    def test_init_name_missing_error(self):
        serializer = RecipeFormSerializer(
            data={},
            context={
                "user": self.USER,
            },
        )
        self.assertFalse(serializer.is_valid())

    def test_init(self):
        serializer = RecipeFormSerializer(
            data={
                "name": "Test",
            },
            context={
                "user": self.USER,
            },
        )
        self.assertTrue(serializer.is_valid())

    def test_values_with_existing_recipe(self):
        serializer = RecipeFormSerializer(
            data={
                "name": "Test",
            },
            context={
                "user": self.USER,
                "lrecipe": self.LRECIPE,
            },
        )
        self.assertTrue(serializer.is_valid())
