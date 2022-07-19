from __future__ import annotations

from django.test import TestCase
from rest_framework.renderers import JSONRenderer

from nutrition_tracker.models import user_ingredient, user_recipe
from nutrition_tracker.serializers import UserRecipeMutableSerializer
from nutrition_tracker.tests import objects as test_objects


class TestSerializersUserRecipeMutable(TestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()

        lfood = test_objects.get_user_ingredient()
        lrecipe = test_objects.get_recipe()
        ufm = test_objects.get_user_food_membership(lrecipe, lfood)
        ufmp = test_objects.get_user_food_membership_portion(ufm)

        lrecipe_2 = test_objects.get_recipe_2()
        ufm2 = test_objects.get_user_food_membership(lrecipe, lrecipe_2)
        ufm2p = test_objects.get_user_food_membership_portion(ufm2)
        cls.USER_RECIPE_PORTION = test_objects.get_user_recipe_portion()

        cls.USER_INGREDIENT = user_ingredient.load_lfood(cls.USER, external_id=lfood.external_id)
        cls.USER_INGREDIENT_MEMBERSHIP = ufm
        cls.USER_INGREDIENT_MEMBERSHIP_PORTION = ufmp
        cls.USER_MEMBER_RECIPE = user_recipe.load_lrecipe(cls.USER, external_id=lrecipe_2.external_id)
        cls.USER_MEMBER_RECIPE_MEMBERSHIP = ufm2
        cls.USER_MEMBER_RECIPE_MEMBERSHIP_PORTION = ufm2p
        cls.USER_RECIPE = user_recipe.load_lrecipe(cls.USER, external_id=lrecipe.external_id)

        cls.SERIALIZED_USER_RECIPE = UserRecipeMutableSerializer(
            instance=cls.USER_RECIPE,
            context={
                "lparent": cls.USER_RECIPE,
                "lfoods": [cls.USER_INGREDIENT],
                "lrecipes": [cls.USER_MEMBER_RECIPE],
            },
        )

    def test_contains_expected_fields(self):
        data = self.SERIALIZED_USER_RECIPE.data
        self.assertEqual(
            set(data.keys()),
            {
                "external_id",
                "name",
                "recipe_date",
                "portions",
                "member_ingredients",
                "member_recipes",
            },
        )

    def test_external_id_content(self):
        data = self.SERIALIZED_USER_RECIPE.data
        self.assertEqual(data["external_id"], str(self.USER_RECIPE.external_id))

    def test_name_content(self):
        data = self.SERIALIZED_USER_RECIPE.data
        self.assertEqual(data["name"], self.USER_RECIPE.name)

    def test_recipe_date_content(self):
        data = self.SERIALIZED_USER_RECIPE.data
        self.assertEqual(data["recipe_date"], str(self.USER_RECIPE.recipe_date))

    def test_display_portions_content(self):
        data = self.SERIALIZED_USER_RECIPE.data
        self.assertJSONEqual(
            JSONRenderer().render(data["portions"]),
            [
                {
                    "id": self.USER_RECIPE_PORTION.id,
                    "external_id": str(self.USER_RECIPE_PORTION.external_id),
                    "household_quantity": None,
                    "household_unit": None,
                    "serving_size": 200.0,
                    "serving_size_unit": "g",
                    "servings_per_container": None,
                },
            ],
        )

    def test_member_ingredients_content(self):
        data = self.SERIALIZED_USER_RECIPE.data
        self.assertJSONEqual(
            JSONRenderer().render(data["member_ingredients"]),
            [
                {
                    "id": self.USER_INGREDIENT_MEMBERSHIP.id,
                    "external_id": str(self.USER_INGREDIENT_MEMBERSHIP.external_id),
                    "child_id": self.USER_INGREDIENT.id,
                    "child_name": self.USER_INGREDIENT.display_name,
                    "child_external_id": str(self.USER_INGREDIENT.external_id),
                    "child_portion_external_id": "-2",
                    "child_portion_name": "1g",
                    "quantity": 50.0,
                }
            ],
        )

    def test_member_recipes_content(self):
        data = self.SERIALIZED_USER_RECIPE.data
        self.assertJSONEqual(
            JSONRenderer().render(data["member_recipes"]),
            [
                {
                    "id": self.USER_MEMBER_RECIPE_MEMBERSHIP.id,
                    "external_id": str(self.USER_MEMBER_RECIPE_MEMBERSHIP.external_id),
                    "child_id": self.USER_MEMBER_RECIPE.id,
                    "child_name": self.USER_MEMBER_RECIPE.name,
                    "child_external_id": str(self.USER_MEMBER_RECIPE.external_id),
                    "child_portion_external_id": "-2",
                    "child_portion_name": "1g",
                    "quantity": 50.0,
                }
            ],
        )
