from __future__ import annotations

import uuid
from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from nutrition_tracker.tests import constants as test_constants
from nutrition_tracker.utils import planner


class TestUtilsPlanner(SimpleTestCase):
    def test_get_quantity_variable(self):
        base_id = "abc"
        expected_output = "abc:q1"
        self.assertEqual(expected_output, planner.get_quantity_variable(base_id))

    def test_get_quantity_variable_day_none(self):
        base_id = "abc"
        expected_output = "abc:q"
        self.assertEqual(expected_output, planner.get_quantity_variable(base_id, day=None))

    def test_is_quantity_variable(self):
        variable_name = "abc:q"
        self.assertTrue(planner.is_quantity_variable(variable_name))

    def test_is_not_quantity_variable(self):
        variable_name = "abc"
        self.assertFalse(planner.is_quantity_variable(variable_name))

    def test_get_presence_variable(self):
        base_id = "abc"
        expected_output = "abc:p1"
        self.assertEqual(expected_output, planner.get_presence_variable(base_id))

    def test_get_presence_variable_day_none(self):
        base_id = "abc"
        expected_output = "abc:p"
        self.assertEqual(expected_output, planner.get_presence_variable(base_id, day=None))

    def test_is_presence_variable(self):
        variable_name = "abc:p"
        self.assertTrue(planner.is_presence_variable(variable_name))

    def test_is_not_presence_variable(self):
        variable_name = "abc"
        self.assertFalse(planner.is_presence_variable(variable_name))

    def test_get_sum_variable(self):
        base_id = "abc"
        expected_output = "abc:s1"
        self.assertEqual(expected_output, planner.get_sum_variable(base_id))

    def test_get_sum_variable_day_none(self):
        base_id = "abc"
        expected_output = "abc:s"
        self.assertEqual(expected_output, planner.get_sum_variable(base_id, day=None))

    def test_is_sum_variable(self):
        variable_name = "abc:s"
        self.assertTrue(planner.is_sum_variable(variable_name))

    def test_is_not_sum_variable(self):
        variable_name = "abc"
        self.assertFalse(planner.is_sum_variable(variable_name))

    @patch(target="uuid.uuid4", new=Mock(return_value=uuid.UUID(test_constants.TEST_UUID)))
    def test_get_constraint_variable(self):
        base_id = "abc"
        expected_output = "abc-%s:c1" % test_constants.TEST_UUID
        self.assertEqual(expected_output, planner.get_constraint_variable(base_id))

    @patch(target="uuid.uuid4", new=Mock(return_value=uuid.UUID(test_constants.TEST_UUID)))
    def test_get_constraint_variable_day_none(self):
        base_id = "abc"
        expected_output = "abc-%s:c" % test_constants.TEST_UUID
        self.assertEqual(expected_output, planner.get_constraint_variable(base_id, day=None))

    def test_is_constraint_variable(self):
        variable_name = "abc:c"
        self.assertTrue(planner.is_constraint_variable(variable_name))

    def test_is_not_constraint_variable(self):
        variable_name = "abc"
        self.assertFalse(planner.is_constraint_variable(variable_name))
