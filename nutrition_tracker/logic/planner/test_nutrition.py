from __future__ import annotations

from django.test import TestCase
from ortools.sat.python import cp_model

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import food_nutrient
from nutrition_tracker.logic.planner import nutrition
from nutrition_tracker.models import user_meal, user_preference
from nutrition_tracker.tests import objects as test_objects
from nutrition_tracker.utils import planner as planner_utils


class TestLogicPlannerNutritionSetupNutritionConstraints(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.USER_INGREDIENT = test_objects.get_user_ingredient()
        test_objects.get_user_food_nutrient()
        cls.USER_MEAL = test_objects.get_meal_today_1()
        ufm = test_objects.get_user_food_membership(cls.USER_MEAL, cls.USER_INGREDIENT)
        test_objects.get_user_food_membership_portion(ufm)
        cls.PREFERENCE = test_objects.get_nutrient_preference()

    def test_setup(self):
        model = cp_model.CpModel()
        variables = {}
        quantity_variable = planner_utils.get_quantity_variable(self.USER_INGREDIENT.external_id)
        variables[quantity_variable] = model.NewIntVar(0, 100, quantity_variable)
        foods_nutrients = food_nutrient.get_foods_nutrients(self.USER, lfoods=[self.USER_INGREDIENT])
        todays_lmeals = user_meal.load_lmeals(self.USER, external_ids=[self.USER_MEAL.external_id])
        preference = user_preference.load_luser_preference(
            self.USER, food_nutrient_id=self.PREFERENCE.food_nutrient_id
        )
        nutrition.setup_nutrition_constraints(
            model, variables, [self.USER_INGREDIENT], [], [], foods_nutrients, [preference], todays_lmeals
        )
        model_proto = model.Proto()
        self.assertEqual(7, len(model_proto.constraints))
        self.assertEqual(4, len(model_proto.variables))
        self.assertTrue(planner_utils.is_presence_variable(model_proto.variables[1].name))
        self.assertTrue(planner_utils.is_quantity_variable(model_proto.variables[2].name))
        self.assertTrue(planner_utils.is_constraint_variable(model_proto.variables[3].name))


class TestLogicPlannerNutritionSetupHistoryConstraints(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.USER_INGREDIENT = test_objects.get_user_ingredient()
        test_objects.get_user_food_nutrient()
        cls.USER_MEAL = test_objects.get_meal_today_1()
        ufm = test_objects.get_user_food_membership(cls.USER_MEAL, cls.USER_INGREDIENT)
        test_objects.get_user_food_membership_portion(ufm)

    def test_setup(self):
        model = cp_model.CpModel()
        variables = {}
        variables["1008:q1"] = model.NewIntVar(0, 100, "1008:q1")
        foods_nutrients = food_nutrient.get_foods_nutrients(self.USER, lfoods=[self.USER_INGREDIENT])
        todays_lmeals = user_meal.load_lmeals(self.USER, external_ids=[self.USER_MEAL.external_id])
        nutrition._setup_history_constraints(
            model, variables, foods_nutrients, constants.ENERGY_NUTRIENT_ID, todays_lmeals
        )
        model_proto = model.Proto()
        self.assertEqual(1, len(model_proto.constraints))
        self.assertEqual(1, len(model_proto.variables))
        self.assertEqual(5000000, model_proto.constraints[0].linear.domain[0])
        self.assertEqual(cp_model.INT_MAX, model_proto.constraints[0].linear.domain[1])


class TestLogicPlannerNutritionSetupPreferenceConstraints(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.PREFERENCE = test_objects.get_nutrient_preference()

    def test_setup(self):
        model = cp_model.CpModel()
        variables = {}
        variables["1008:q1"] = model.NewIntVar(0, 100, "1008:q1")
        preference = user_preference.load_luser_preference(
            self.USER, food_nutrient_id=self.PREFERENCE.food_nutrient_id
        )
        nutrition._setup_preference_constraints(model, variables, preference)
        model_proto = model.Proto()
        self.assertEqual(3, len(model_proto.constraints))
        self.assertEqual(2, len(model_proto.variables))
        self.assertTrue(planner_utils.is_constraint_variable(model_proto.variables[1].name))
        self.assertEqual(1, model_proto.constraints[0].enforcement_literal[0])
        self.assertEqual(100000000, model_proto.constraints[0].linear.domain[0])
        self.assertEqual(cp_model.INT_MAX, model_proto.constraints[0].linear.domain[1])
        self.assertEqual(-2, model_proto.constraints[1].enforcement_literal[0])
        self.assertEqual(cp_model.INT_MIN, model_proto.constraints[1].linear.domain[0])
        self.assertEqual(99999999, model_proto.constraints[1].linear.domain[1])
        self.assertEqual(1, model_proto.constraints[2].linear.domain[0])
        self.assertEqual(1, model_proto.constraints[2].linear.domain[1])
