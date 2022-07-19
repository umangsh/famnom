"""User details serializer module."""
from __future__ import annotations

from typing import Any

from dj_rest_auth.serializers import UserDetailsSerializer
from rest_framework import serializers

import users.models as user_model
from nutrition_tracker.biz import user


class UserDataSerializer(UserDetailsSerializer):
    """User details metadata serializer class."""

    is_pregnant = serializers.NullBooleanField()
    family_members = serializers.SerializerMethodField()
    new_family_member = serializers.EmailField(write_only=True, required=False)

    class Meta(UserDetailsSerializer.Meta):
        fields = (
            "external_id",
            "first_name",
            "last_name",
            "email",
            "date_of_birth",
            "is_pregnant",
            "family_members",
            "new_family_member",
        )
        read_only_fields = ("external_id",)

    def get_family_members(self, obj: user_model.User) -> list[str]:  # pylint: disable=no-self-use
        """Returns family member emails as list."""
        return [luser.email for luser in list(user.get_family_members(obj))]

    def update(self, instance: user_model.User, validated_data: dict[str, Any]) -> user_model.User:
        """Update user model."""
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.email = validated_data.get("email", instance.email)
        instance.date_of_birth = validated_data.get("date_of_birth", instance.date_of_birth)

        if instance.is_pregnant() != validated_data.get("is_pregnant"):
            instance.update_flag(user_model.User.FLAG_IS_PREGNANT, bool(validated_data.get("is_pregnant")))
        instance.save()

        new_family_member = validated_data.get("new_family_member")
        if new_family_member:
            user.create_family(instance, new_family_member)

        return instance
