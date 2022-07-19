from __future__ import annotations

from unittest.mock import patch

from django.test import TestCase
from ortools.sat.python import cp_model

from nutrition_tracker.constants import constants
from nutrition_tracker.logic.planner import category
from nutrition_tracker.models import user_meal, user_preference
from nutrition_tracker.tests import objects as test_objects
from nutrition_tracker.utils import planner as planner_utils


class TestLogicPlannerCategorySetupMemberCountThresholdConstraints(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.CATEGORY = test_objects.get_category()
        cls.PREFERENCE = test_objects.get_category_preference()

    def test_setup(self):
        model = cp_model.CpModel()
        variables = {}
        sum_variable = planner_utils.get_sum_variable(self.CATEGORY.id_)
        variables[sum_variable] = model.NewIntVar(0, 100, sum_variable)
        preference = user_preference.load_luser_preference(self.USER, food_category_id=self.CATEGORY.id_)
        preference_threshold = preference.userpreferencethreshold_set.all().first()
        preference_threshold.dimension = constants.Dimension.COUNT
        preference_threshold.expansion_set = constants.ExpansionSet.MEMBERS
        preference_threshold.save()
        preference = user_preference.load_luser_preference(self.USER, food_category_id=self.CATEGORY.id_)

        category._setup_member_count_threshold_constraints(model, variables, self.CATEGORY, preference)
        model_proto = model.Proto()
        self.assertEqual(2, len(model_proto.constraints))
        self.assertEqual(2, len(model_proto.variables))
        self.assertTrue(planner_utils.is_constraint_variable(model_proto.variables[1].name))
        self.assertEqual(1, model_proto.constraints[0].enforcement_literal[0])
        self.assertEqual(50, model_proto.constraints[0].linear.domain[0])
        self.assertEqual(cp_model.INT_MAX, model_proto.constraints[0].linear.domain[1])
        self.assertEqual(-2, model_proto.constraints[1].enforcement_literal[0])
        self.assertEqual(cp_model.INT_MIN, model_proto.constraints[1].linear.domain[0])
        self.assertEqual(49, model_proto.constraints[1].linear.domain[1])


class TestLogicPlannerCategorySetupSelfCountThresholdConstraints(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.CATEGORY = test_objects.get_category()
        cls.PREFERENCE = test_objects.get_category_preference()

    def test_setup(self):
        model = cp_model.CpModel()
        variables = {}
        presence_variable = planner_utils.get_presence_variable(self.CATEGORY.id_)
        variables[presence_variable] = model.NewBoolVar(presence_variable)
        preference = user_preference.load_luser_preference(self.USER, food_category_id=self.CATEGORY.id_)
        preference_threshold = preference.userpreferencethreshold_set.all().first()
        preference_threshold.dimension = constants.Dimension.COUNT
        preference_threshold.expansion_set = constants.ExpansionSet.SELF
        preference_threshold.save()
        preference = user_preference.load_luser_preference(self.USER, food_category_id=self.CATEGORY.id_)

        category._setup_self_count_threshold_constraints(model, variables, self.CATEGORY, preference)
        model_proto = model.Proto()
        self.assertEqual(2, len(model_proto.constraints))
        self.assertEqual(2, len(model_proto.variables))
        self.assertTrue(planner_utils.is_constraint_variable(model_proto.variables[1].name))
        self.assertEqual(1, model_proto.constraints[0].enforcement_literal[0])
        self.assertEqual(50, model_proto.constraints[0].linear.domain[0])
        self.assertEqual(cp_model.INT_MAX, model_proto.constraints[0].linear.domain[1])
        self.assertEqual(-2, model_proto.constraints[1].enforcement_literal[0])
        self.assertEqual(cp_model.INT_MIN, model_proto.constraints[1].linear.domain[0])
        self.assertEqual(49, model_proto.constraints[1].linear.domain[1])


class TestLogicPlannerCategorySetupCountThresholdConstraints(TestCase):
    @patch.object(category, "_setup_self_count_threshold_constraints")
    @patch.object(category, "_setup_member_count_threshold_constraints")
    def test_setup(self, mock_1, mock_2):
        category._setup_count_threshold_constraints(
            cp_model.CpModel(), {}, test_objects.get_category(), test_objects.get_category_preference()
        )
        self.assertTrue(mock_1.called)
        self.assertTrue(mock_2.called)


class TestLogicPlannerCategorySetupMemberQuantityThresholdConstraints(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.CATEGORY = test_objects.get_category()
        cls.USER_INGREDIENT = test_objects.get_user_ingredient()
        cls.PREFERENCE = test_objects.get_category_preference()
        cls.FOOD_PREFERENCE = test_objects.get_user_preference()

    def test_setup(self):
        model = cp_model.CpModel()
        variables = {}
        presence_variable = planner_utils.get_presence_variable(self.USER_INGREDIENT.external_id)
        variables[presence_variable] = model.NewBoolVar(presence_variable)
        quantity_variable = planner_utils.get_quantity_variable(self.USER_INGREDIENT.external_id)
        variables[quantity_variable] = model.NewIntVar(0, 100, quantity_variable)
        preference = user_preference.load_luser_preference(self.USER, food_category_id=self.CATEGORY.id_)
        preference_threshold = preference.userpreferencethreshold_set.all().first()
        preference_threshold.dimension = constants.Dimension.QUANTITY
        preference_threshold.expansion_set = constants.ExpansionSet.MEMBERS
        preference_threshold.save()
        preference = user_preference.load_luser_preference(self.USER, food_category_id=self.CATEGORY.id_)

        category._setup_member_quantity_threshold_constraints(
            model, variables, [self.USER_INGREDIENT], preference, [self.FOOD_PREFERENCE]
        )
        model_proto = model.Proto()
        self.assertEqual(2, len(model_proto.constraints))
        self.assertEqual(3, len(model_proto.variables))
        self.assertEqual(-1, model_proto.constraints[0].enforcement_literal[0])
        self.assertEqual(0, model_proto.constraints[0].linear.domain[0])
        self.assertEqual(0, model_proto.constraints[0].linear.domain[1])
        self.assertEqual(0, model_proto.constraints[1].enforcement_literal[0])
        self.assertEqual(1, model_proto.constraints[1].linear.domain[0])
        self.assertEqual(cp_model.INT_MAX, model_proto.constraints[1].linear.domain[1])


class TestLogicPlannerCategorySetupSelfQuantityThresholdConstraints(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.CATEGORY = test_objects.get_category()
        cls.PREFERENCE = test_objects.get_category_preference()

    def test_setup(self):
        model = cp_model.CpModel()
        variables = {}
        presence_variable = planner_utils.get_presence_variable(self.CATEGORY.id_)
        variables[presence_variable] = model.NewBoolVar(presence_variable)
        quantity_variable = planner_utils.get_quantity_variable(self.CATEGORY.id_)
        variables[quantity_variable] = model.NewIntVar(0, 100, quantity_variable)
        preference = user_preference.load_luser_preference(self.USER, food_category_id=self.CATEGORY.id_)
        preference_threshold = preference.userpreferencethreshold_set.all().first()
        preference_threshold.dimension = constants.Dimension.QUANTITY
        preference_threshold.expansion_set = constants.ExpansionSet.SELF
        preference_threshold.save()
        preference = user_preference.load_luser_preference(self.USER, food_category_id=self.CATEGORY.id_)

        category._setup_self_quantity_threshold_constraints(model, variables, self.CATEGORY, preference)
        model_proto = model.Proto()
        self.assertEqual(2, len(model_proto.constraints))
        self.assertEqual(3, len(model_proto.variables))
        self.assertEqual(-1, model_proto.constraints[0].enforcement_literal[0])
        self.assertEqual(0, model_proto.constraints[0].linear.domain[0])
        self.assertEqual(0, model_proto.constraints[0].linear.domain[1])
        self.assertEqual(0, model_proto.constraints[1].enforcement_literal[0])
        self.assertEqual(1, model_proto.constraints[1].linear.domain[0])
        self.assertEqual(cp_model.INT_MAX, model_proto.constraints[1].linear.domain[1])


class TestLogicPlannerCategorySetupQuantityThresholdConstraints(TestCase):
    @patch.object(category, "_setup_self_quantity_threshold_constraints")
    @patch.object(category, "_setup_member_quantity_threshold_constraints")
    def test_setup(self, mock_1, mock_2):
        category._setup_quantity_threshold_constraints(
            cp_model.CpModel(),
            {},
            test_objects.get_category(),
            [test_objects.get_user_ingredient()],
            test_objects.get_category_preference(),
            [test_objects.get_user_preference()],
        )
        self.assertTrue(mock_1.called)
        self.assertTrue(mock_2.called)


class TestLogicPlannerCategorySetupThresholdConstraints(TestCase):
    @patch.object(category, "_setup_quantity_threshold_constraints")
    @patch.object(category, "_setup_count_threshold_constraints")
    def test_setup(self, mock_1, mock_2):
        category._setup_threshold_constraints(
            cp_model.CpModel(),
            {},
            test_objects.get_category(),
            [test_objects.get_user_ingredient()],
            test_objects.get_category_preference(),
            [test_objects.get_user_preference()],
        )
        self.assertTrue(mock_1.called)
        self.assertTrue(mock_2.called)


class TestLogicPlannerCategorySetupPreferenceConstraints(TestCase):
    @patch.object(category, "_setup_threshold_constraints")
    def test_setup(self, mock):
        category._setup_preference_constraints(
            cp_model.CpModel(),
            {},
            test_objects.get_category(),
            [test_objects.get_user_ingredient()],
            test_objects.get_category_preference(),
            [test_objects.get_user_preference()],
        )
        self.assertTrue(mock.called)


class TestLogicPlannerCategorySetupHistoryConstraints(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.CATEGORY = test_objects.get_category()
        cls.USER_INGREDIENT = test_objects.get_user_ingredient()
        cls.USER_MEAL = test_objects.get_meal_today_1()
        ufm = test_objects.get_user_food_membership(cls.USER_MEAL, cls.USER_INGREDIENT)
        test_objects.get_user_food_membership_portion(ufm)

    def test_setup(self):
        model = cp_model.CpModel()
        variables = {}
        quantity_variable = planner_utils.get_quantity_variable(self.CATEGORY.id_)
        variables[quantity_variable] = model.NewIntVar(0, 100, quantity_variable)
        sum_variable = planner_utils.get_sum_variable(self.CATEGORY.id_)
        variables[sum_variable] = model.NewIntVar(0, 100, sum_variable)
        todays_lmeals = user_meal.load_lmeals(self.USER, external_ids=[self.USER_MEAL.external_id])

        category._setup_history_constraints(model, variables, self.CATEGORY, [self.USER_INGREDIENT], todays_lmeals)
        model_proto = model.Proto()
        self.assertEqual(2, len(model_proto.constraints))
        self.assertEqual(2, len(model_proto.variables))
        self.assertEqual(50, model_proto.constraints[0].linear.domain[0])
        self.assertEqual(cp_model.INT_MAX, model_proto.constraints[0].linear.domain[1])
        self.assertEqual(1, model_proto.constraints[1].linear.domain[0])
        self.assertEqual(cp_model.INT_MAX, model_proto.constraints[1].linear.domain[1])


class TestLogicPlannerCategorySetupCategoryConstraints(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.CATEGORY = test_objects.get_category()
        cls.USER_INGREDIENT = test_objects.get_user_ingredient()
        cls.PREFERENCE = test_objects.get_category_preference()
        cls.FOOD_PREFERENCE = test_objects.get_user_preference()
        cls.USER_MEAL = test_objects.get_meal_today_1()
        ufm = test_objects.get_user_food_membership(cls.USER_MEAL, cls.USER_INGREDIENT)
        test_objects.get_user_food_membership_portion(ufm)

    def test_setup(self):
        model = cp_model.CpModel()
        variables = {}
        presence_variable = planner_utils.get_presence_variable(self.USER_INGREDIENT.external_id)
        variables[presence_variable] = model.NewBoolVar(presence_variable)
        quantity_variable = planner_utils.get_quantity_variable(self.USER_INGREDIENT.external_id)
        variables[quantity_variable] = model.NewIntVar(0, 100, quantity_variable)
        todays_lmeals = user_meal.load_lmeals(self.USER, external_ids=[self.USER_MEAL.external_id])

        category.setup_category_constraints(
            model,
            variables,
            [self.USER_INGREDIENT],
            [self.CATEGORY],
            [self.FOOD_PREFERENCE],
            [self.PREFERENCE],
            todays_lmeals,
        )
        model_proto = model.Proto()
        self.assertEqual(12, len(model_proto.constraints))
        self.assertEqual(7, len(model_proto.variables))
