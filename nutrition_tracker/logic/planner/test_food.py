from __future__ import annotations

from unittest.mock import patch

from django.test import TestCase
from ortools.sat.python import cp_model

from nutrition_tracker.constants import constants
from nutrition_tracker.logic import data_loaders
from nutrition_tracker.logic.planner import food
from nutrition_tracker.models import user_meal, user_preference, user_recipe
from nutrition_tracker.tests import objects as test_objects
from nutrition_tracker.utils import planner as planner_utils


class TestLogicPlannerFoodSetupCountThresholdConstraints(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.USER_INGREDIENT = test_objects.get_user_ingredient()
        cls.PREFERENCE = test_objects.get_user_preference()

    def test_setup(self):
        model = cp_model.CpModel()
        variables = {}
        presence_variable = planner_utils.get_presence_variable(self.USER_INGREDIENT.external_id)
        variables[presence_variable] = model.NewIntVar(0, 100, presence_variable)
        preference = user_preference.load_luser_preference(
            self.USER, food_external_id=self.PREFERENCE.food_external_id
        )
        preference_threshold = preference.userpreferencethreshold_set.all().first()
        preference_threshold.dimension = constants.Dimension.COUNT
        preference_threshold.save()
        preference = user_preference.load_luser_preference(
            self.USER, food_external_id=self.PREFERENCE.food_external_id
        )

        food._setup_count_threshold_constraints(model, variables, self.USER_INGREDIENT, preference)
        model_proto = model.Proto()
        self.assertEqual(2, len(model_proto.constraints))
        self.assertEqual(2, len(model_proto.variables))
        self.assertTrue(planner_utils.is_constraint_variable(model_proto.variables[1].name))
        self.assertEqual(1, model_proto.constraints[0].enforcement_literal[0])
        self.assertEqual(5, model_proto.constraints[0].linear.domain[0])
        self.assertEqual(cp_model.INT_MAX, model_proto.constraints[0].linear.domain[1])
        self.assertEqual(-2, model_proto.constraints[1].enforcement_literal[0])
        self.assertEqual(cp_model.INT_MIN, model_proto.constraints[1].linear.domain[0])
        self.assertEqual(4, model_proto.constraints[1].linear.domain[1])


class TestLogicPlannerFoodSetupQuantityThresholdConstraints(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.USER_INGREDIENT = test_objects.get_user_ingredient()
        cls.PREFERENCE = test_objects.get_user_preference()

    def test_setup(self):
        model = cp_model.CpModel()
        variables = {}
        presence_variable = planner_utils.get_presence_variable(self.USER_INGREDIENT.external_id)
        variables[presence_variable] = model.NewBoolVar(presence_variable)
        preference = user_preference.load_luser_preference(
            self.USER, food_external_id=self.PREFERENCE.food_external_id
        )

        food._setup_quantity_threshold_constraints(model, variables, self.USER_INGREDIENT, preference, 0, 1)
        model_proto = model.Proto()
        self.assertEqual(3, len(model_proto.constraints))
        self.assertEqual(2, len(model_proto.variables))
        self.assertTrue(planner_utils.is_quantity_variable(model_proto.variables[1].name))
        self.assertEqual(4, len(model_proto.variables[1].domain))
        self.assertEqual(-1, model_proto.constraints[0].enforcement_literal[0])
        self.assertEqual(0, model_proto.constraints[0].linear.domain[0])
        self.assertEqual(0, model_proto.constraints[0].linear.domain[1])
        self.assertEqual(0, model_proto.constraints[1].enforcement_literal[0])
        self.assertEqual(1, model_proto.constraints[1].linear.domain[0])
        self.assertEqual(cp_model.INT_MAX, model_proto.constraints[1].linear.domain[1])

    def test_setup_with_history(self):
        model = cp_model.CpModel()
        variables = {}
        presence_variable = planner_utils.get_presence_variable(self.USER_INGREDIENT.external_id)
        variables[presence_variable] = model.NewBoolVar(presence_variable)
        quantity_variable = planner_utils.get_quantity_variable(self.USER_INGREDIENT.external_id)
        variables[quantity_variable] = model.NewIntVar(0, 100, quantity_variable)
        preference = user_preference.load_luser_preference(
            self.USER, food_external_id=self.PREFERENCE.food_external_id
        )

        food._setup_quantity_threshold_constraints(model, variables, self.USER_INGREDIENT, preference, 2, 2)
        model_proto = model.Proto()
        self.assertEqual(2, len(model_proto.constraints))
        self.assertEqual(3, len(model_proto.variables))


class TestLogicPlannerFoodSetupThresholdConstraints(TestCase):
    @patch.object(food, "_setup_quantity_threshold_constraints")
    @patch.object(food, "_setup_count_threshold_constraints")
    def test_setup(self, mock_1, mock_2):
        food._setup_threshold_constraints(
            cp_model.CpModel(), {}, test_objects.get_user_ingredient(), test_objects.get_user_preference(), 2, 2
        )
        self.assertTrue(mock_1.called)
        self.assertTrue(mock_2.called)


class TestLogicPlannerFoodSetupPreferenceConstraints(TestCase):
    @patch.object(food, "_setup_threshold_constraints")
    def test_setup(self, mock):
        food._setup_preference_constraints(
            cp_model.CpModel(), {}, test_objects.get_user_ingredient(), test_objects.get_user_preference(), 2, 2
        )
        self.assertTrue(mock.called)


class TestLogicPlannerFoodSetupAvailableQuantityConstraints(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.USER_INGREDIENT = test_objects.get_user_ingredient()

    def test_food_noop(self):
        model = cp_model.CpModel()
        variables = {}
        object_type_id = data_loaders.get_content_type_ingredient_id()
        food._setup_available_quantity_constraints(model, variables, self.USER_INGREDIENT, object_type_id)
        self.assertEqual(f"{model.Proto()}", "")

    def test_recipe_constraints(self):
        model = cp_model.CpModel()
        variables = {}
        lrecipe = test_objects.get_recipe()
        test_objects.get_user_recipe_portion()
        lrecipe = user_recipe.load_lrecipe(self.USER, external_id=lrecipe.external_id)
        object_type_id = data_loaders.get_content_type_recipe_id()
        quantity_variable = planner_utils.get_quantity_variable(lrecipe.external_id)
        variables[quantity_variable] = model.NewIntVar(0, 100, quantity_variable)
        food._setup_available_quantity_constraints(model, variables, lrecipe, object_type_id)
        model_proto = model.Proto()
        self.assertEqual(cp_model.INT_MIN, model_proto.constraints[0].linear.domain[0])
        self.assertEqual(200, model_proto.constraints[0].linear.domain[1])


class TestLogicPlannerFoodSetupHistoryConstraints(TestCase):
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
        quantity_variable = planner_utils.get_quantity_variable(self.USER_INGREDIENT.external_id)
        variables[quantity_variable] = model.NewIntVar(0, 100, quantity_variable)
        todays_lmeals = user_meal.load_lmeals(self.USER, external_ids=[self.USER_MEAL.external_id])
        object_type_id = data_loaders.get_content_type_ingredient_id()
        food._setup_history_constraints(model, variables, self.USER_INGREDIENT, todays_lmeals, object_type_id)

        model_proto = model.Proto()
        self.assertEqual(1, len(model_proto.constraints))
        self.assertEqual(1, len(model_proto.variables))
        self.assertEqual(50, model_proto.constraints[0].linear.domain[0])
        self.assertEqual(cp_model.INT_MAX, model_proto.constraints[0].linear.domain[1])


class TestLogicPlannerFoodSetupFoodConstraints(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.USER_INGREDIENT = test_objects.get_user_ingredient()
        test_objects.get_user_food_nutrient()
        cls.USER_MEAL = test_objects.get_meal_today_1()
        ufm = test_objects.get_user_food_membership(cls.USER_MEAL, cls.USER_INGREDIENT)
        test_objects.get_user_food_membership_portion(ufm)
        cls.PREFERENCE = test_objects.get_user_preference()

    def test_setup(self):
        model = cp_model.CpModel()
        variables = {}
        todays_lmeals = user_meal.load_lmeals(self.USER, external_ids=[self.USER_MEAL.external_id])
        object_type_id = data_loaders.get_content_type_ingredient_id()
        food.setup_food_constraints(
            model, variables, [self.USER_INGREDIENT], [self.PREFERENCE], todays_lmeals, object_type_id
        )

        model_proto = model.Proto()
        self.assertEqual(6, len(model_proto.constraints))
        self.assertEqual(3, len(model_proto.variables))
