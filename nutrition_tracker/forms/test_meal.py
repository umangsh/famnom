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
    MealForm,
    RecipeMemberFormset,
)
from nutrition_tracker.logic import data_loaders
from nutrition_tracker.models import user_food_membership, user_food_portion, user_meal
from nutrition_tracker.tests import objects as test_objects
from nutrition_tracker.tests import utils as test_utils


class TestFormsMealForm(TransactionTestCase):
    reset_sequences = True
    maxDiff = None

    def setUp(self):
        self.USER = test_objects.get_user()
        self.USER_MEAL = test_objects.get_meal_today_1()

    def test_form_empty_init(self):
        kwargs = {"user": self.USER}
        form = MealForm(**kwargs)
        food_members = FoodMemberFormset(prefix="food")
        recipe_members = RecipeMemberFormset(prefix="recipe")

        context = {
            "food_members": food_members,
            "food_members_helper": CreateFoodMemberFormsetHelper(food_members),
            "recipe_members": recipe_members,
            "recipe_members_helper": CreateRecipeMemberFormsetHelper(recipe_members),
        }
        with open("%s/test_form_meal_empty_init.txt" % test_utils.get_golden_dir()) as golden:
            expected_output = golden.read().replace("{TODAY_DATE}", str(timezone.localdate()))
            self.assertHTMLEqual(expected_output, render_crispy_form(form, context=context))

    def test_form_lmeal_blank_init(self):
        kwargs = {"user": self.USER, "lmeal": self.USER_MEAL}
        form = MealForm(**kwargs)
        food_members = FoodMemberFormset(prefix="food")
        recipe_members = RecipeMemberFormset(prefix="recipe")

        context = {
            "food_members": food_members,
            "food_members_helper": CreateFoodMemberFormsetHelper(food_members),
            "recipe_members": recipe_members,
            "recipe_members_helper": CreateRecipeMemberFormsetHelper(recipe_members),
        }
        with open("%s/test_form_lmeal_blank_init.txt" % test_utils.get_golden_dir()) as golden:
            expected_output = (
                golden.read()
                .replace("{TODAY_DATE}", str(timezone.localdate()))
                .replace("{MEAL_EXTERNAL_ID}", str(self.USER_MEAL.external_id))
            )
            self.assertHTMLEqual(expected_output, render_crispy_form(form, context=context))

    def test_form_lmeal_with_members_init(self):
        lfood = test_objects.get_user_ingredient()
        lrecipe = test_objects.get_recipe()
        ufm1 = test_objects.get_user_food_membership(self.USER_MEAL, lfood)
        test_objects.get_user_food_membership_portion(ufm1)
        ufm2 = test_objects.get_user_food_membership(self.USER_MEAL, lrecipe)
        test_objects.get_user_food_membership_portion(ufm2)

        # Load objects with members
        lmeal = user_meal.load_lmeal(self.USER, id_=self.USER_MEAL.id)
        lfoods = data_loaders.load_lfoods_for_lparents(self.USER, [lmeal])
        member_recipes = data_loaders.load_lrecipes_for_lparents(self.USER, [lmeal])

        kwargs = {"user": self.USER, "lmeal": lmeal}
        form = MealForm(**kwargs)
        food_members = FoodMemberFormset(
            instance=lmeal,
            prefix="food",
            queryset=user_food_membership.load_lmemberships(
                self.USER,
                parent_id=lmeal.id,
                parent_type_id=data_loaders.get_content_type_meal_id(),
                child_type_id=data_loaders.get_content_type_ingredient_id(),
            ),
            form_kwargs={"lparent": lmeal, "lfoods": lfoods},
        )
        recipe_members = RecipeMemberFormset(
            instance=lmeal,
            prefix="recipe",
            queryset=user_food_membership.load_lmemberships(
                self.USER,
                parent_id=lmeal.id,
                parent_type_id=data_loaders.get_content_type_meal_id(),
                child_type_id=data_loaders.get_content_type_recipe_id(),
            ),
            form_kwargs={"lparent": lmeal, "lrecipes": member_recipes},
        )

        context = {
            "food_members": food_members,
            "food_members_helper": EditFoodMemberFormsetHelper(food_members),
            "recipe_members": recipe_members,
            "recipe_members_helper": EditRecipeMemberFormsetHelper(recipe_members),
        }
        with open("%s/test_form_lmeal_with_members_init.txt" % test_utils.get_golden_dir()) as golden:
            expected_output = (
                golden.read()
                .replace("{TODAY_DATE}", str(timezone.localdate()))
                .replace("{MEAL_EXTERNAL_ID}", str(self.USER_MEAL.external_id))
                .replace("{FOOD_EXTERNAL_ID}", str(lfood.external_id))
                .replace("{RECIPE_EXTERNAL_ID}", str(lrecipe.external_id))
            )
            self.assertHTMLEqual(expected_output, render_crispy_form(form, context=context))

    def test_form_lmeal_with_members_save(self):
        lfood = test_objects.get_user_ingredient()
        lrecipe = test_objects.get_recipe()

        # Load objects with members
        lmeal = user_meal.load_lmeal(self.USER, id_=self.USER_MEAL.id)
        lfoods = data_loaders.load_lfoods_for_lparents(self.USER, [lmeal])
        member_recipes = data_loaders.load_lrecipes_for_lparents(self.USER, [lmeal])

        form_data = {
            # Metadata fields
            "meal_type": constants.MealType.BREAKFAST,
            "meal_date": timezone.localdate(),
            # Foods management form data
            "food-TOTAL_FORMS": "1",
            "food-INITIAL_FORMS": "0",
            "food-MIN_NUM_FORMS": "0",
            "food-MAX_NUM_FORMS": "1000",
            # First food
            "food-0-child_external_id": lfood.external_id,
            "food-0-quantity": 3,
            "food-0-serving": -2,
            # Recipes management form data
            "recipe-TOTAL_FORMS": "1",
            "recipe-INITIAL_FORMS": "0",
            "recipe-MIN_NUM_FORMS": "0",
            "recipe-MAX_NUM_FORMS": "1000",
            # First recipe
            "recipe-0-child_external_id": lrecipe.external_id,
            "recipe-0-quantity": 7,
            "recipe-0-serving": -1,
        }
        kwargs = {"user": self.USER, "lmeal": lmeal}
        form = MealForm(data=form_data, **kwargs)
        food_members = FoodMemberFormset(
            form_data, instance=lmeal, prefix="food", form_kwargs={"lparent": lmeal, "lfoods": lfoods}
        )
        recipe_members = RecipeMemberFormset(
            form_data, instance=lmeal, prefix="recipe", form_kwargs={"lparent": lmeal, "lrecipes": member_recipes}
        )

        self.assertTrue(form.is_valid())
        self.assertTrue(food_members.is_valid())
        self.assertTrue(recipe_members.is_valid())
        form.save(food_members, recipe_members)
        self.assertEqual(2, user_food_portion.load_lfood_portions(self.USER).count())
        self.assertEqual(2, user_food_membership.load_lmemberships(self.USER).count())

    def test_form_lmeal_with_members_family_save(self):
        lfood = test_objects.get_user_ingredient()
        lrecipe = test_objects.get_recipe()
        lfood_2 = test_objects.get_user_2_ingredient()
        luser_2 = test_objects.get_user_2()
        user.create_family(self.USER, luser_2.email)
        self.USER.refresh_from_db()
        luser_2.refresh_from_db()

        kwargs = {"user": self.USER}
        form_data = {
            # Metadata fields
            "meal_type": constants.MealType.BREAKFAST,
            "meal_date": timezone.localdate(),
            # Foods management form data
            "food-TOTAL_FORMS": "2",
            "food-INITIAL_FORMS": "0",
            "food-MIN_NUM_FORMS": "0",
            "food-MAX_NUM_FORMS": "1000",
            # First food
            "food-0-child_external_id": lfood.external_id,
            "food-0-quantity": 3,
            "food-0-serving": -2,
            # Second food
            "food-1-child_external_id": lfood_2.external_id,
            "food-1-quantity": 5,
            "food-1-serving": -1,
            # Recipes management form data
            "recipe-TOTAL_FORMS": "1",
            "recipe-INITIAL_FORMS": "0",
            "recipe-MIN_NUM_FORMS": "0",
            "recipe-MAX_NUM_FORMS": "1000",
            # First recipe
            "recipe-0-child_external_id": lrecipe.external_id,
            "recipe-0-quantity": 7,
            "recipe-0-serving": -1,
        }
        form = MealForm(data=form_data, **kwargs)
        food_members = FoodMemberFormset(form_data, prefix="food")
        recipe_members = RecipeMemberFormset(form_data, prefix="recipe")

        self.assertTrue(form.is_valid())
        self.assertTrue(food_members.is_valid())
        self.assertTrue(recipe_members.is_valid())
        form.save(food_members, recipe_members)
        self.assertEqual(3, user_food_portion.load_lfood_portions(self.USER).count())
        self.assertEqual(3, user_food_membership.load_lmemberships(self.USER).count())
        self.assertEqual(3, user_food_portion.load_lfood_portions(luser_2).count())
        self.assertEqual(3, user_food_membership.load_lmemberships(luser_2).count())
