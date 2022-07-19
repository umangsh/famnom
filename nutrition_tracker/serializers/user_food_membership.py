"""UserFoodMembership serializer module."""
from __future__ import annotations

from rest_framework import serializers

from nutrition_tracker.logic import data_loaders, food_portion
from nutrition_tracker.models import UserFoodMembership
from nutrition_tracker.serializers import base


class UserFoodMembershipSerializer(base.NonNullModelSerializer):
    """UserFoodMembership Serializer class."""

    child_external_id = serializers.SerializerMethodField()
    child_name = serializers.SerializerMethodField()
    child_portion_external_id = serializers.SerializerMethodField()
    child_portion_name = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()

    class Meta:
        model = UserFoodMembership
        fields = (
            "id",
            "external_id",
            "child_id",
            "child_name",
            "child_external_id",
            "child_portion_external_id",
            "child_portion_name",
            "quantity",
        )

    def get_child_external_id(self, obj: UserFoodMembership) -> str | None:
        """Get child external ID to be rendered in recipe/meal forms."""
        lfoods = self.context.get("lfoods", [])
        lrecipes = self.context.get("lrecipes", [])

        if obj.child_type_id == data_loaders.get_content_type_ingredient_id():
            lobject = next((lfood for lfood in lfoods if lfood.id == obj.child_id), None)
            if lobject:
                return str(lobject.external_id)

        if obj.child_type_id == data_loaders.get_content_type_recipe_id():
            lobject = next((lrecipe for lrecipe in lrecipes if lrecipe.id == obj.child_id), None)
            if lobject:
                return str(lobject.external_id)

        return None

    def get_child_name(self, obj: UserFoodMembership) -> str | None:
        """Get child name to be rendered in recipe/meal forms."""
        lfoods = self.context.get("lfoods", [])
        lrecipes = self.context.get("lrecipes", [])

        if obj.child_type_id == data_loaders.get_content_type_ingredient_id():
            lobject = next((lfood for lfood in lfoods if lfood.id == obj.child_id), None)
            if lobject:
                return lobject.display_name

        if obj.child_type_id == data_loaders.get_content_type_recipe_id():
            lobject = next((lrecipe for lrecipe in lrecipes if lrecipe.id == obj.child_id), None)
            if lobject:
                return lobject.name

        return None

    def _populate_child_portion_and_quantity(self, obj: UserFoodMembership) -> tuple:
        """Get child portion external ID and quantity to be rendered in recipe/meal forms."""
        lparent = self.context.get("lparent", None)
        lfoods = self.context.get("lfoods", [])
        lrecipes = self.context.get("lrecipes", [])

        lobject = None
        cfood = None
        if obj.child_type_id == data_loaders.get_content_type_ingredient_id():
            lobject = next((lfood for lfood in lfoods if lfood.id == obj.child_id), None)
            cfood = lobject.db_food if lobject else None
        elif obj.child_type_id == data_loaders.get_content_type_recipe_id():
            lobject = next((lrecipe for lrecipe in lrecipes if lrecipe.id == obj.child_id), None)

        if not lobject:
            return (), None

        food_portions = food_portion.for_display_choices(lobject, cfood=cfood)
        if lparent:
            member_portion = next((member.portions[0] for member in lparent.members if member.id == obj.id), None)
            if member_portion:
                portion = food_portion.get_food_member_portion(member_portion, food_portions)
                if portion:
                    fp_tuple, quantity = portion
                    return fp_tuple, quantity

        return (), None

    def get_child_portion_external_id(self, obj: UserFoodMembership) -> str | None:
        """Get child portion external ID to be rendered in recipe/meal forms."""
        fp_tuple, unused_quantity = self._populate_child_portion_and_quantity(obj)
        if fp_tuple:
            return str(fp_tuple[0])

        return None

    def get_child_portion_name(self, obj: UserFoodMembership) -> str | None:
        """Get child portion name to be rendered in recipe/meal forms."""
        fp_tuple, unused_quantity = self._populate_child_portion_and_quantity(obj)
        if fp_tuple:
            return str(fp_tuple[1])

        return None

    def get_quantity(self, obj: UserFoodMembership) -> str | None:
        """Get quantity to be rendered in recipe/meal forms."""
        unused_fp_tuple, quantity = self._populate_child_portion_and_quantity(obj)
        return quantity
