from __future__ import annotations

from datetime import datetime

from django.test import SimpleTestCase
from django.utils import timezone

from nutrition_tracker.tests import constants as test_constants
from nutrition_tracker.utils import text


class TestUtilsTextTitle(SimpleTestCase):
    def test_title_empty(self):
        string = ""
        expected_output = ""
        self.assertEqual(expected_output, text.title(string))

    def test_title_no_changes(self):
        string = "Milk A&D"
        expected_output = "Milk A&d"
        self.assertEqual(expected_output, text.title(string))

    def test_title(self):
        string = "mILk a&d"
        expected_output = "Milk A&d"
        self.assertEqual(expected_output, text.title(string))


class TestUtilsTextFormatDate(SimpleTestCase):
    def test_format_date_today(self):
        date = timezone.localdate()
        expected_output = "Today"
        self.assertEqual(expected_output, text.format_date(date))

    def test_format_date(self):
        date = timezone.make_aware(datetime.strptime("22-05-2020", "%d-%m-%Y")).date()
        expected_output = "Fri, 22 May 2020"
        self.assertEqual(expected_output, text.format_date(date))


class TestUtilsTextIsValidUUID(SimpleTestCase):
    def test_is_valid_uuid(self):
        string = test_constants.TEST_UUID
        self.assertTrue(text.is_valid_uuid(string))

    def test_is_invalid_uuid(self):
        string = "abc"
        self.assertFalse(text.is_valid_uuid(string))


class TestUtilsTextValidFloat(SimpleTestCase):
    def test_valid_float(self):
        value = 4.333
        expected_output = float(4.333)
        self.assertEqual(expected_output, text.valid_float(value))

    def test_invalid_float(self):
        value = "abc"
        self.assertIsNone(text.valid_float(value))
