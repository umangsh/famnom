from __future__ import annotations

from django.test import SimpleTestCase

from nutrition_tracker.serializers import UUIDSerializer
from nutrition_tracker.tests import constants as test_constants


class TestSerializersUUIDSerializer(SimpleTestCase):
    def test_valid_id(self):
        serializer = UUIDSerializer(data={"id": test_constants.TEST_UUID})
        self.assertTrue(serializer.is_valid())

    def test_invalid_id(self):
        serializer = UUIDSerializer(data={"id": "invalid"})
        self.assertFalse(serializer.is_valid())
