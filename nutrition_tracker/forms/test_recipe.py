from __future__ import annotations

from crispy_forms.utils import render_crispy_form
from django.test import TransactionTestCase
from django.utils import timezone

from nutrition_tracker.biz import user
from nutrition_tracker.constants import constants
from nutrition_tracker.forms import (
    CreateFoodMemberFormsetHelper,
    CreateRecipeMemberFormsetHelper,
    EditFoodMemberFormsetHelper,
    EditRecipeMemberFormsetHelper,
    FoodMemberFormset,
    FoodPortionFormset,
    FoodPortionRecipeFormsetHelper,
    RecipeForm,
    RecipeMemberFormset,
)
from nutrition_tracker.logic import data_loaders
from nutrition_tracker.models import user_food_membership, user_food_portion, user_recipe
from nutrition_tracker.tests import objects as test_objects
from nutrition_tracker.tests import utils as test_utils


class TestFormsRecipeForm(TransactionTestCase):
    reset_sequences = True
    maxDiff = None

    def setUp(self):
        self.USER = test_objects.get_user()
        self.USER_RECIPE = test_objects.get_recipe()

    def test_form_empty_init(self):
        kwargs = {"user": self.USER}
        form = RecipeForm(**kwargs)
        servings = FoodPortionFormset(prefix="servings")
        food_members = FoodMemberFormset(prefix="food")
        recipe_members = RecipeMemberFormset(prefix="recipe")

        context = {
            "servings": servings,
            "servings_helper": FoodPortionRecipeFormsetHelper(servings),
            "food_members": food_members,
            "food_members_helper": CreateFoodMemberFormsetHelper(food_members),
            "recipe_members": recipe_members,
            "recipe_members_helper": CreateRecipeMemberFormsetHelper(recipe_members),
        }
        with open("%s/test_form_recipe_empty_init.txt" % test_utils.get_golden_dir()) as golden:
            expected_output = golden.read().replace("{TODAY_DATE}", str(timezone.localdate()))
            self.assertHTMLEqual(expected_output, render_crispy_form(form, context=context))

    def test_form_lrecipe_blank_init(self):
        kwargs = {"user": self.USER, "lrecipe": self.USER_RECIPE}
        form = RecipeForm(**kwargs)
        servings = FoodPortionFormset(prefix="servings")
        food_members = FoodMemberFormset(prefix="food")
        recipe_members = RecipeMemberFormset(prefix="recipe")

        context = {
            "servings": servings,
            "servings_helper": FoodPortionRecipeFormsetHelper(servings),
            "food_members": food_members,
            "food_members_helper": CreateFoodMemberFormsetHelper(food_members),
            "recipe_members": recipe_members,
            "recipe_members_helper": CreateRecipeMemberFormsetHelper(recipe_members),
        }
        with open("%s/test_form_lrecipe_blank_init.txt" % test_utils.get_golden_dir()) as golden:
            expected_output = (
                golden.read()
                .replace("{TODAY_DATE}", str(timezone.localdate()))
                .replace("{RECIPE_EXTERNAL_ID}", str(self.USER_RECIPE.external_id))
            )
            self.assertHTMLEqual(expected_output, render_crispy_form(form, context=context))

    def test_form_lrecipe_with_defaults_init(self):
        lfood = test_objects.get_user_ingredient()
        lrecipe_2 = test_objects.get_recipe_2()
        ufm1 = test_objects.get_user_food_membership(self.USER_RECIPE, lfood)
        test_objects.get_user_food_membership_portion(ufm1)
        ufm2 = test_objects.get_user_food_membership(self.USER_RECIPE, lrecipe_2)
        test_objects.get_user_food_membership_portion(ufm2)
        test_objects.get_user_recipe_portion()

        # Load objects with members
        lrecipe = user_recipe.load_lrecipe(self.USER, id_=self.USER_RECIPE.id)
        lfoods = data_loaders.load_lfoods_for_lparents(self.USER, [lrecipe])
        member_recipes = data_loaders.load_lrecipes_for_lparents(self.USER, [lrecipe])

        kwargs = {"user": self.USER, "lrecipe": lrecipe}
        form = RecipeForm(**kwargs)
        servings = FoodPortionFormset(instance=lrecipe, prefix="servings")
        food_members = FoodMemberFormset(
            instance=lrecipe,
            prefix="food",
            queryset=user_food_membership.load_lmemberships(
                self.USER,
                parent_id=lrecipe.id,
                parent_type_id=data_loaders.get_content_type_recipe_id(),
                child_type_id=data_loaders.get_content_type_ingredient_id(),
            ),
            form_kwargs={"lparent": lrecipe, "lfoods": lfoods},
        )
        recipe_members = RecipeMemberFormset(
            instance=lrecipe,
            prefix="recipe",
            queryset=user_food_membership.load_lmemberships(
                self.USER,
                parent_id=lrecipe.id,
                parent_type_id=data_loaders.get_content_type_recipe_id(),
                child_type_id=data_loaders.get_content_type_recipe_id(),
            ),
            form_kwargs={"lparent": lrecipe, "lrecipes": member_recipes},
        )

        context = {
            "servings": servings,
            "servings_helper": FoodPortionRecipeFormsetHelper(servings),
            "food_members": food_members,
            "food_members_helper": EditFoodMemberFormsetHelper(food_members),
            "recipe_members": recipe_members,
            "recipe_members_helper": EditRecipeMemberFormsetHelper(recipe_members),
        }
        with open("%s/test_form_lrecipe_with_defaults_init.txt" % test_utils.get_golden_dir()) as golden:
            expected_output = (
                golden.read()
                .replace("{TODAY_DATE}", str(timezone.localdate()))
                .replace("{RECIPE_EXTERNAL_ID}", str(self.USER_RECIPE.external_id))
                .replace("{FOOD_EXTERNAL_ID}", str(lfood.external_id))
                .replace("{RECIPE_2_EXTERNAL_ID}", str(lrecipe_2.external_id))
            )
            self.assertHTMLEqual(expected_output, render_crispy_form(form, context=context))

    def test_form_lrecipe_save(self):
        lfood = test_objects.get_user_ingredient()
        lrecipe_2 = test_objects.get_recipe_2()
        ufm1 = test_objects.get_user_food_membership(self.USER_RECIPE, lfood)
        test_objects.get_user_food_membership_portion(ufm1)
        ufm2 = test_objects.get_user_food_membership(self.USER_RECIPE, lrecipe_2)
        test_objects.get_user_food_membership_portion(ufm2)
        lrecipe_portion = test_objects.get_user_recipe_portion()

        # Load objects with members
        lrecipe = user_recipe.load_lrecipe(self.USER, id_=self.USER_RECIPE.id)
        lfoods = data_loaders.load_lfoods_for_lparents(self.USER, [lrecipe])
        member_recipes = data_loaders.load_lrecipes_for_lparents(self.USER, [lrecipe])

        # New items added to recipe
        lfood_2 = test_objects.get_user_ingredient_2()

        form_data = {
            # Metadata fields
            "name": "Updated Name",
            "recipe_date": lrecipe.recipe_date,
            # Foods management form data
            "food-TOTAL_FORMS": "2",
            "food-INITIAL_FORMS": "1",
            "food-MIN_NUM_FORMS": "0",
            "food-MAX_NUM_FORMS": "1000",
            # First food (existing)
            "food-0-id": lfood.id,
            "food-0-child_external_id": lfood.external_id,
            "food-0-quantity": 50,
            "food-0-serving": -2,
            # Second food (new)
            "food-1-child_external_id": lfood_2.external_id,
            "food-1-quantity": 3,
            "food-1-serving": -3,
            # Recipes management form data
            "recipe-TOTAL_FORMS": "1",
            "recipe-INITIAL_FORMS": "1",
            "recipe-MIN_NUM_FORMS": "0",
            "recipe-MAX_NUM_FORMS": "1000",
            # First recipe (existing)
            "recipe-0-id": lrecipe_2.id,
            "recipe-0-child_external_id": lrecipe_2.external_id,
            "recipe-0-quantity": 50,
            "recipe-0-serving": -2,
            # Servings management form data
            "servings-TOTAL_FORMS": "2",
            "servings-INITIAL_FORMS": "1",
            "servings-MIN_NUM_FORMS": "0",
            "servings-MAX_NUM_FORMS": "1000",
            # First serving (existing)
            "servings-0-id": lrecipe_portion.id,
            "servings-0-serving_size": 200,
            "servings-0-serving_size_unit": constants.ServingSizeUnit.WEIGHT,
            # Servings (new)
            "servings-1-serving_size": 150,
            "servings-1-serving_size_unit": constants.ServingSizeUnit.WEIGHT,
            "servings-1-household_quantity": "1/8",
            "servings-1-measure_unit": 1000,
        }

        kwargs = {"user": self.USER, "lrecipe": lrecipe}
        form = RecipeForm(data=form_data, **kwargs)
        servings = FoodPortionFormset(form_data, instance=lrecipe, prefix="servings")
        food_members = FoodMemberFormset(
            form_data,
            instance=lrecipe,
            prefix="food",
            queryset=user_food_membership.load_lmemberships(
                self.USER,
                parent_id=lrecipe.id,
                parent_type_id=data_loaders.get_content_type_recipe_id(),
                child_type_id=data_loaders.get_content_type_ingredient_id(),
            ),
            form_kwargs={"lparent": lrecipe, "lfoods": lfoods},
        )
        recipe_members = RecipeMemberFormset(
            form_data,
            instance=lrecipe,
            prefix="recipe",
            queryset=user_food_membership.load_lmemberships(
                self.USER,
                parent_id=lrecipe.id,
                parent_type_id=data_loaders.get_content_type_recipe_id(),
                child_type_id=data_loaders.get_content_type_recipe_id(),
            ),
            form_kwargs={"lparent": lrecipe, "lrecipes": member_recipes},
        )

        self.assertTrue(form.is_valid())
        self.assertTrue(servings.is_valid())
        self.assertTrue(food_members.is_valid())
        self.assertTrue(recipe_members.is_valid())
        form.save(servings, food_members, recipe_members)

        lrecipe.refresh_from_db()
        self.assertEqual("Updated Name", lrecipe.name)
        self.assertEqual(5, user_food_portion.load_lfood_portions(self.USER).count())
        self.assertEqual(3, user_food_membership.load_lmemberships(self.USER).count())

    def test_form_lrecipe_family_save(self):
        lfood = test_objects.get_user_ingredient()
        lfood_2 = test_objects.get_user_2_ingredient()
        luser_2 = test_objects.get_user_2()
        user.create_family(self.USER, luser_2.email)
        self.USER.refresh_from_db()
        luser_2.refresh_from_db()

        form_data = {
            # Metadata fields
            "name": "Recipe Name",
            "recipe_date": timezone.localdate(),
            # Foods management form data
            "food-TOTAL_FORMS": "2",
            "food-INITIAL_FORMS": "0",
            "food-MIN_NUM_FORMS": "0",
            "food-MAX_NUM_FORMS": "1000",
            # First food
            "food-0-child_external_id": lfood.external_id,
            "food-0-quantity": 50,
            "food-0-serving": -2,
            # Second food
            "food-1-child_external_id": lfood_2.external_id,
            "food-1-quantity": 3,
            "food-1-serving": -3,
            # Recipes management form data
            "recipe-TOTAL_FORMS": "0",
            "recipe-INITIAL_FORMS": "0",
            "recipe-MIN_NUM_FORMS": "0",
            "recipe-MAX_NUM_FORMS": "1000",
            # Servings management form data
            "servings-TOTAL_FORMS": "1",
            "servings-INITIAL_FORMS": "0",
            "servings-MIN_NUM_FORMS": "0",
            "servings-MAX_NUM_FORMS": "1000",
            # First serving
            "servings-0-serving_size": 200,
            "servings-0-serving_size_unit": constants.ServingSizeUnit.WEIGHT,
        }

        kwargs = {"user": self.USER}
        form = RecipeForm(data=form_data, **kwargs)
        servings = FoodPortionFormset(form_data, prefix="servings")
        food_members = FoodMemberFormset(form_data, prefix="food")
        recipe_members = RecipeMemberFormset(form_data, prefix="recipe")

        self.assertTrue(form.is_valid())
        self.assertTrue(servings.is_valid())
        self.assertTrue(food_members.is_valid())
        self.assertTrue(recipe_members.is_valid())
        form.save(servings, food_members, recipe_members)
        self.assertEqual(3, user_food_portion.load_lfood_portions(self.USER).count())
        self.assertEqual(2, user_food_membership.load_lmemberships(self.USER).count())
        self.assertEqual(3, user_food_portion.load_lfood_portions(luser_2).count())
        self.assertEqual(2, user_food_membership.load_lmemberships(luser_2).count())
