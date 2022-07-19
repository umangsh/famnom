from __future__ import annotations

from django.test import TestCase

from nutrition_tracker.models import user_food_membership, user_ingredient, user_recipe
from nutrition_tracker.serializers import UserFoodMembershipSerializer
from nutrition_tracker.tests import objects as test_objects


class TestSerializersUserFoodPortion(TestCase):
    @classmethod
    def setUpTestData(cls):
        luser = test_objects.get_user()
        lrecipe = test_objects.get_recipe()
        lfood = test_objects.get_user_ingredient()
        ufm = test_objects.get_user_food_membership(lrecipe, lfood)
        test_objects.get_user_food_membership_portion(ufm)

        cls.LPARENT = user_recipe.load_lrecipe(luser, external_id=lrecipe.external_id)
        cls.FOOD_MEMBER = user_ingredient.load_lfood(luser, external_id=lfood.external_id)
        cls.USER_FOOD_MEMBERSHIP = user_food_membership.load_lmembership(luser, id_=ufm.id)
        cls.SERIALIZED_USER_FOOD_MEMBERSHIP = UserFoodMembershipSerializer(
            instance=cls.USER_FOOD_MEMBERSHIP, context={"lparent": cls.LPARENT, "lfoods": [cls.FOOD_MEMBER]}
        )

    def test_contains_expected_fields(self):
        data = self.SERIALIZED_USER_FOOD_MEMBERSHIP.data
        self.assertEqual(
            set(data.keys()),
            {
                "id",
                "external_id",
                "child_id",
                "child_name",
                "child_external_id",
                "child_portion_external_id",
                "child_portion_name",
                "quantity",
            },
        )

    def test_id_content(self):
        data = self.SERIALIZED_USER_FOOD_MEMBERSHIP.data
        self.assertEqual(data["id"], self.USER_FOOD_MEMBERSHIP.id)

    def test_external_id_content(self):
        data = self.SERIALIZED_USER_FOOD_MEMBERSHIP.data
        self.assertEqual(data["external_id"], str(self.USER_FOOD_MEMBERSHIP.external_id))

    def test_child_id_content(self):
        data = self.SERIALIZED_USER_FOOD_MEMBERSHIP.data
        self.assertEqual(data["child_id"], self.FOOD_MEMBER.id)

    def test_child_name_content(self):
        data = self.SERIALIZED_USER_FOOD_MEMBERSHIP.data
        self.assertEqual(data["child_name"], self.FOOD_MEMBER.display_name)

    def test_child_external_id_content(self):
        data = self.SERIALIZED_USER_FOOD_MEMBERSHIP.data
        self.assertEqual(data["child_external_id"], str(self.FOOD_MEMBER.external_id))

    def test_child_portion_external_id_content(self):
        data = self.SERIALIZED_USER_FOOD_MEMBERSHIP.data
        self.assertEqual(data["child_portion_external_id"], "-2")

    def test_quantity_content(self):
        data = self.SERIALIZED_USER_FOOD_MEMBERSHIP.data
        self.assertEqual(data["quantity"], 50.0)
