from __future__ import annotations

from django.test import TestCase
from ortools.sat.python import cp_model

from nutrition_tracker.logic.planner import common
from nutrition_tracker.models import user_meal, user_preference, user_preference_threshold
from nutrition_tracker.tests import objects as test_objects
from nutrition_tracker.utils import planner as planner_utils


class TestLogicPlannerCommonRestrictToRepeatableOrUnused(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.USER_INGREDIENT = test_objects.get_user_ingredient()
        cls.USER_INGREDIENT_2 = test_objects.get_user_ingredient_2()
        cls.USER_RECIPE = test_objects.get_recipe()

    def test_no_matching_foods(self):
        p1 = test_objects.get_user_preference()
        p2 = test_objects.get_user_preference_2()
        p3 = test_objects.get_user_recipe_preference()

        external_ids = [
            self.USER_INGREDIENT.external_id,
            self.USER_INGREDIENT_2.external_id,
            self.USER_RECIPE.external_id,
        ]
        preferences = [p1, p2, p3]
        self.assertCountEqual(external_ids, common.restrict_to_repeatable_or_unused(external_ids, preferences, [], []))

    def test_with_repeatable_items(self):
        p1 = test_objects.get_user_preference()
        p2 = test_objects.get_user_preference_2()
        p3 = test_objects.get_user_recipe_preference()

        external_ids = [
            self.USER_INGREDIENT.external_id,
            self.USER_INGREDIENT_2.external_id,
            self.USER_RECIPE.external_id,
        ]
        preferences = [p1, p2, p3]
        self.assertCountEqual(
            external_ids,
            common.restrict_to_repeatable_or_unused(
                external_ids, preferences, [self.USER_INGREDIENT, self.USER_INGREDIENT_2], [self.USER_RECIPE]
            ),
        )

    def test_with_non_repeatable_but_not_consumed_previously_items(self):
        p1 = user_preference.create(self.USER, food_external_id=self.USER_INGREDIENT.external_id)
        p1.add_flag(user_preference.FLAG_IS_NOT_REPEATABLE)
        p1.save()

        p2 = user_preference.create(self.USER, food_external_id=self.USER_INGREDIENT_2.external_id)
        p2.add_flag(user_preference.FLAG_IS_NOT_REPEATABLE)
        p2.save()

        p3 = user_preference.create(self.USER, food_external_id=self.USER_RECIPE.external_id)
        p3.add_flag(user_preference.FLAG_IS_NOT_REPEATABLE)
        p3.save()

        external_ids = [
            self.USER_INGREDIENT.external_id,
            self.USER_INGREDIENT_2.external_id,
            self.USER_RECIPE.external_id,
        ]
        preferences = [p1, p2, p3]
        self.assertCountEqual(external_ids, common.restrict_to_repeatable_or_unused(external_ids, preferences, [], []))

    def test_with_non_repeatable_with_previously_consumed_items(self):
        p1 = user_preference.create(self.USER, food_external_id=self.USER_INGREDIENT.external_id)
        p1.add_flag(user_preference.FLAG_IS_NOT_REPEATABLE)
        p1.save()

        p2 = test_objects.get_user_preference_2()
        p3 = user_preference.create(self.USER, food_external_id=self.USER_RECIPE.external_id)
        p3.add_flag(user_preference.FLAG_IS_NOT_REPEATABLE)
        p3.save()

        external_ids = [self.USER_INGREDIENT_2.external_id]
        preferences = [p1, p2, p3]
        self.assertCountEqual(
            external_ids,
            common.restrict_to_repeatable_or_unused(
                external_ids, preferences, [self.USER_INGREDIENT, self.USER_INGREDIENT_2], [self.USER_RECIPE]
            ),
        )


class TestLogicPlannerCommonAddFromHistory(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.USER_INGREDIENT = test_objects.get_user_ingredient()
        cls.USER_RECIPE = test_objects.get_recipe()
        cls.USER_MEAL = test_objects.get_meal_today_1()
        cls.USER_MEAL_2 = test_objects.get_meal_today_2()
        cls.USER_INGREDIENT_2 = test_objects.get_user_ingredient_2()
        test_objects.get_user_food_membership(cls.USER_MEAL, cls.USER_INGREDIENT_2)
        test_objects.get_user_food_membership(cls.USER_MEAL, cls.USER_RECIPE)

    def test_add_from_history_no_meals(self):
        self.assertCountEqual([], common.add_from_history([], [], [self.USER_INGREDIENT], [self.USER_RECIPE]))

    def test_add_from_history_with_meals(self):
        todays_lmeals = user_meal.load_lmeals(self.USER, external_ids=[self.USER_MEAL_2.external_id])
        self.assertCountEqual(
            [], common.add_from_history([], todays_lmeals, [self.USER_INGREDIENT], [self.USER_RECIPE])
        )

    def test_add_from_history_with_meals_extra_foods(self):
        external_ids = [self.USER_INGREDIENT_2.external_id, self.USER_RECIPE.external_id]
        todays_lmeals = user_meal.load_lmeals(
            self.USER, external_ids=[self.USER_MEAL_2.external_id, self.USER_MEAL.external_id]
        )
        self.assertCountEqual(
            list(external_ids),
            common.add_from_history(
                [], todays_lmeals, [self.USER_INGREDIENT, self.USER_INGREDIENT_2], [self.USER_RECIPE]
            ),
        )


class TestLogicPlannerCommonSetupThresholdConstraintBase(TestCase):
    def test_threshold_exact(self):
        model = cp_model.CpModel()
        variables = {}
        variable_name = "test"
        variables[variable_name] = model.NewIntVar(0, 100, variable_name)
        base_id = 123
        threshold = user_preference_threshold.UserPreferenceThreshold(exact_value=43)
        common.setup_threshold_constraint_base(model, variables, variable_name, base_id, threshold)
        model_proto = model.Proto()
        self.assertEqual(2, len(model_proto.constraints))
        self.assertEqual(2, len(model_proto.variables))
        self.assertTrue(planner_utils.is_constraint_variable(model_proto.variables[1].name))
        self.assertEqual(1, model_proto.constraints[0].enforcement_literal[0])
        self.assertEqual(43, model_proto.constraints[0].linear.domain[0])
        self.assertEqual(43, model_proto.constraints[0].linear.domain[1])
        self.assertEqual(-2, model_proto.constraints[1].enforcement_literal[0])
        self.assertEqual(cp_model.INT_MIN, model_proto.constraints[1].linear.domain[0])
        self.assertEqual(42, model_proto.constraints[1].linear.domain[1])
        self.assertEqual(44, model_proto.constraints[1].linear.domain[2])
        self.assertEqual(cp_model.INT_MAX, model_proto.constraints[1].linear.domain[3])

    def test_threshold_min(self):
        model = cp_model.CpModel()
        variables = {}
        variable_name = "test"
        variables[variable_name] = model.NewIntVar(0, 100, variable_name)
        base_id = 123
        threshold = user_preference_threshold.UserPreferenceThreshold(min_value=43)
        common.setup_threshold_constraint_base(model, variables, variable_name, base_id, threshold)
        model_proto = model.Proto()
        self.assertEqual(2, len(model_proto.constraints))
        self.assertEqual(2, len(model_proto.variables))
        self.assertTrue(planner_utils.is_constraint_variable(model_proto.variables[1].name))
        self.assertEqual(1, model_proto.constraints[0].enforcement_literal[0])
        self.assertEqual(43, model_proto.constraints[0].linear.domain[0])
        self.assertEqual(cp_model.INT_MAX, model_proto.constraints[0].linear.domain[1])
        self.assertEqual(-2, model_proto.constraints[1].enforcement_literal[0])
        self.assertEqual(cp_model.INT_MIN, model_proto.constraints[1].linear.domain[0])
        self.assertEqual(42, model_proto.constraints[1].linear.domain[1])

    def test_threshold_max(self):
        model = cp_model.CpModel()
        variables = {}
        variable_name = "test"
        variables[variable_name] = model.NewIntVar(0, 100, variable_name)
        base_id = 123
        threshold = user_preference_threshold.UserPreferenceThreshold(max_value=43)
        common.setup_threshold_constraint_base(
            model, variables, variable_name, base_id, threshold, history=53, multiplier=2, enforce_exact=True
        )
        model_proto = model.Proto()
        self.assertEqual(3, len(model_proto.constraints))
        self.assertEqual(2, len(model_proto.variables))
        self.assertTrue(planner_utils.is_constraint_variable(model_proto.variables[1].name))
        self.assertEqual(1, model_proto.constraints[0].enforcement_literal[0])
        self.assertEqual(cp_model.INT_MIN, model_proto.constraints[0].linear.domain[0])
        self.assertEqual(106, model_proto.constraints[0].linear.domain[1])
        self.assertEqual(-2, model_proto.constraints[1].enforcement_literal[0])
        self.assertEqual(107, model_proto.constraints[1].linear.domain[0])
        self.assertEqual(cp_model.INT_MAX, model_proto.constraints[1].linear.domain[1])
        self.assertEqual(1, model_proto.constraints[2].linear.domain[0])
        self.assertEqual(1, model_proto.constraints[2].linear.domain[1])


class TestLogicPlannerCommonSetupDefaultFoodConstraints(TestCase):
    def test_setup(self):
        model = cp_model.CpModel()
        variables = {}
        variable_name = "test"
        variables[variable_name] = model.NewIntVar(0, 100, variable_name)
        history = 53
        common.setup_default_food_constraints(model, variables, variable_name, history)

        model_proto = model.Proto()
        self.assertEqual(2, len(model_proto.constraints))
        self.assertEqual(53, model_proto.constraints[0].linear.domain[0])
        self.assertEqual(100, model_proto.constraints[1].linear.domain[1])


class TestLogicPlannerCommonGetThresholdIntervals(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()
        cls.p1 = test_objects.get_user_preference()
        cls.p2 = test_objects.get_user_preference_2()
        cls.p3 = test_objects.get_nutrient_preference()

    def test_get_food_threshold_intervals_default(self):
        self.assertCountEqual([[10, 100]], common.get_threshold_intervals(self.p1, None))

    def test_get_nutrient_threshold_intervals_default(self):
        self.assertCountEqual([[0, 5000]], common.get_threshold_intervals(self.p3, None))

    def test_get_food_threshold_intervals(self):
        p1 = user_preference.load_luser_preference(self.USER, food_external_id=self.p1.food_external_id)
        self.assertCountEqual(
            [[5, 100]], common.get_threshold_intervals(p1, p1.userpreferencethreshold_set.all().first())
        )

    def test_get_nutrient_threshold_intervals(self):
        p3 = user_preference.load_luser_preference(self.USER, food_nutrient_id=self.p3.food_nutrient_id)
        self.assertCountEqual(
            [[1000, 5000]], common.get_threshold_intervals(p3, p3.userpreferencethreshold_set.all().first())
        )
