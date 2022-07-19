from __future__ import annotations

from unittest.mock import patch

from django.test import TestCase
from ortools.sat.python import cp_model

from nutrition_tracker.logic import mealplan
from nutrition_tracker.tests import objects as test_objects
from nutrition_tracker.utils import planner as planner_utils


class TestLogicMealplanGetMealplanFromSolution(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_INGREDIENT = test_objects.get_user_ingredient()
        cls.USER_RECIPE = test_objects.get_recipe()

    def test_invalid_mealplan(self):
        self.assertEqual(
            {},
            mealplan._get_mealplan_from_solution(
                cp_model.CpSolver(), cp_model.MODEL_INVALID, {}, [self.USER_INGREDIENT], [self.USER_RECIPE]
            ),
        )

    def test_infeasible_mealplan(self):
        self.assertEqual(
            {},
            mealplan._get_mealplan_from_solution(
                cp_model.CpSolver(), cp_model.INFEASIBLE, {}, [self.USER_INGREDIENT], [self.USER_RECIPE]
            ),
        )

    def test_unknown_mealplan(self):
        self.assertEqual(
            {},
            mealplan._get_mealplan_from_solution(
                cp_model.CpSolver(), cp_model.UNKNOWN, {}, [self.USER_INGREDIENT], [self.USER_RECIPE]
            ),
        )

    @patch.object(cp_model.CpSolver, "Value", return_value=4)
    def test_valid_mealplan(self, mock):
        model = cp_model.CpModel()
        variables = {}
        presence_variable = planner_utils.get_presence_variable(self.USER_INGREDIENT.external_id)
        variables[presence_variable] = model.NewBoolVar(presence_variable)
        presence_variable = planner_utils.get_presence_variable(self.USER_RECIPE.external_id)
        variables[presence_variable] = model.NewBoolVar(presence_variable)
        quantity_variable = planner_utils.get_quantity_variable(self.USER_INGREDIENT.external_id)
        variables[quantity_variable] = model.NewIntVar(0, 100, quantity_variable)
        quantity_variable = planner_utils.get_quantity_variable(self.USER_RECIPE.external_id)
        variables[quantity_variable] = model.NewIntVar(0, 100, quantity_variable)
        self.assertEqual(
            len(
                mealplan._get_mealplan_from_solution(
                    cp_model.CpSolver(), cp_model.OPTIMAL, variables, [self.USER_INGREDIENT], [self.USER_RECIPE]
                )
            ),
            2,
        )


class TestLogicMealplanGetMealplanForUser(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.USER_INGREDIENT = test_objects.get_user_ingredient()
        test_objects.get_user_food_nutrient()
        test_objects.get_user_food_portion()
        cls.USER_INGREDIENT_2 = test_objects.get_user_ingredient_2()
        test_objects.get_user_2_food_nutrient()
        test_objects.get_user_2_food_portion()
        test_objects.get_nutrient_preference()

    def test_valid_mealplan(self):
        lmealplan = mealplan.get_mealplan_for_user(self.USER)
        self.assertFalse(lmealplan.infeasible)
        self.assertEqual(len(lmealplan.quantity_map), 1)
