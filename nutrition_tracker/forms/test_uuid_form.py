from __future__ import annotations

from django.test import SimpleTestCase

from nutrition_tracker.forms import UUIDForm
from nutrition_tracker.tests import constants as test_constants


class TestFormsUUIDForm(SimpleTestCase):
    def test_valid_id(self):
        form = UUIDForm(data={"id": test_constants.TEST_UUID})
        self.assertTrue(form.is_valid())

    def test_empty_id(self):
        form = UUIDForm(data={"id": ""})
        self.assertEqual(form.errors, {"id": ["This field is required."]})

    def test_with_mid(self):
        form = UUIDForm(data={"id": test_constants.TEST_UUID, "mid": test_constants.TEST_UUID_2})
        self.assertTrue(form.is_valid())

    def test_with_nexturl(self):
        form = UUIDForm(data={"id": test_constants.TEST_UUID, "nexturl": "/"})
        self.assertTrue(form.is_valid())
