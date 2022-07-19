from __future__ import annotations

from unittest.mock import patch

from django.test import TestCase

import users.models as user_model
from nutrition_tracker.biz import user
from nutrition_tracker.tests import constants as test_constants
from nutrition_tracker.tests import objects as test_objects
from nutrition_tracker.utils import exceptions


class TestBizUser(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = test_objects.get_user()

    def test_empty_qs(self):
        self.assertFalse(user.empty_qs().exists())

    def test_load_queryset(self):
        self.assertEqual(1, user._load_queryset().count())

    def test_load_luser_no_params(self):
        self.assertIsNone(user.load_luser())

    def test_load_luser_by_id(self):
        self.assertEqual(self.USER, user.load_luser(id_=self.USER.id))

    def test_load_luser_by_external_id(self):
        self.assertEqual(self.USER, user.load_luser(external_id=self.USER.external_id))

    def test_load_luser_by_email(self):
        self.assertEqual(self.USER, user.load_luser(email=self.USER.email))

    def test_load_lusers_no_params(self):
        test_objects.get_user_2()
        self.assertEqual(2, user.load_lusers().count())

    def test_load_lusers_ids_and_emails(self):
        luser_2 = test_objects.get_user_2()
        self.assertEqual(2, user.load_lusers(ids=[self.USER.id], emails=[luser_2.email]).count())

    def test_load_lusers_family_id(self):
        self.USER.family_id = test_constants.TEST_UUID
        self.USER.save()
        luser_2 = test_objects.get_user_2()
        luser_2.family_id = test_constants.TEST_UUID
        luser_2.save()
        self.assertEqual(2, user.load_lusers(family_id=test_constants.TEST_UUID).count())

    def test_get_flags(self):
        self.assertEqual(1, user.get_flags({user_model.User.FLAG_IS_PREGNANT: True}))

    def test_create_family_same_user(self):
        user.create_family(self.USER, self.USER.email)
        self.USER.refresh_from_db()
        self.assertIsNone(self.USER.family_id)

    def test_create_family_missing_email(self):
        user.create_family(self.USER, "unknownemail@abc.com")
        self.USER.refresh_from_db()
        self.assertIsNone(self.USER.family_id)

    def test_create_family(self):
        self.assertIsNone(self.USER.family_added_timestamp)
        luser_2 = test_objects.get_user_2()
        user.create_family(self.USER, luser_2.email)
        luser_2.refresh_from_db()
        self.USER.refresh_from_db()
        self.assertIsNotNone(self.USER.family_added_timestamp)
        self.assertIsNotNone(self.USER.family_id)
        self.assertIsNotNone(luser_2.family_id)
        self.assertEqual(self.USER.family_id, luser_2.family_id)

    def test_create_family_with_family_id(self):
        self.USER.family_id = test_constants.TEST_UUID
        self.USER.save()
        luser_2 = test_objects.get_user_2()
        user.create_family(self.USER, luser_2.email)
        self.assertEqual(2, user.load_lusers(family_id=test_constants.TEST_UUID).count())

    def test_create_family_child_family_id_raises(self):
        self.USER.family_id = test_constants.TEST_UUID
        self.USER.save()
        self.USER.refresh_from_db()
        luser_2 = test_objects.get_user_2()
        with self.assertRaises(exceptions.UserInAnotherFamilyException):
            user.create_family(luser_2, self.USER.email)

        self.USER.refresh_from_db()
        self.assertEqual(str(self.USER.family_id), test_constants.TEST_UUID)
        luser_2.refresh_from_db()
        self.assertIsNone(luser_2.family_id)

    def test_add_to_family_empty_id(self):
        user.add_to_family(self.USER, "")
        self.USER.refresh_from_db()
        self.assertIsNone(self.USER.family_id)

    def test_add_to_family_valid_id(self):
        self.assertIsNone(self.USER.family_added_timestamp)
        user.add_to_family(self.USER, test_constants.TEST_UUID)
        self.USER.refresh_from_db()
        self.assertEqual(str(self.USER.family_id), test_constants.TEST_UUID)
        self.assertIsNotNone(self.USER.family_added_timestamp)

    def test_add_to_family_valid_id_with_existing_raises(self):
        self.USER.family_id = test_constants.TEST_UUID
        self.USER.save()
        self.USER.refresh_from_db()
        with self.assertRaises(exceptions.UserInAnotherFamilyException):
            user.add_to_family(self.USER, test_constants.TEST_UUID_2)

        self.USER.refresh_from_db()
        self.assertEqual(str(self.USER.family_id), test_constants.TEST_UUID)

    @patch("nutrition_tracker.constants.constants.MAX_FAMILY_SIZE", 1)
    def test_add_to_family_max_size_raises(self):
        self.USER.family_id = test_constants.TEST_UUID
        self.USER.save()
        self.USER.refresh_from_db()
        luser_2 = test_objects.get_user_2()
        with self.assertRaises(exceptions.MaxFamilySizeException):
            user.add_to_family(luser_2, self.USER.family_id)

        self.USER.refresh_from_db()
        self.assertEqual(str(self.USER.family_id), test_constants.TEST_UUID)
        luser_2.refresh_from_db()
        self.assertIsNone(luser_2.family_id)

    def test_add_to_family_valid_id_with_existing_returns(self):
        self.USER.family_id = test_constants.TEST_UUID
        self.USER.save()
        user.add_to_family(self.USER, test_constants.TEST_UUID)
        self.USER.refresh_from_db()
        self.assertEqual(str(self.USER.family_id), test_constants.TEST_UUID)

    def test_get_family_members_no_family_id(self):
        self.assertFalse(user.get_family_members(self.USER).exists())

    def test_get_family_members_with_family_id(self):
        self.USER.family_id = test_constants.TEST_UUID
        self.USER.save()
        user.get_family_members(self.USER)
        self.assertEqual(1, user.get_family_members(self.USER).count())
