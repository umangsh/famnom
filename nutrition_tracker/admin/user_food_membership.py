"""Admin module for user food memberships."""
from __future__ import annotations

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from nutrition_tracker.admin import user_food_portion
from nutrition_tracker.models import UserFoodMembership
from nutrition_tracker.utils import model as model_utils


@admin.register(UserFoodMembership)
class UserFoodMembershipAdmin(admin.ModelAdmin):
    """User Food Membership Admin"""

    fields: list[str] = model_utils.get_field_names(
        list(UserFoodMembership._meta.fields), prefix_fields_in_order=["user"]
    )
    list_display: list[str] = model_utils.get_field_names(
        list(UserFoodMembership._meta.fields), prefix_fields_in_order=["user"]
    )
    ordering = ["id"]
    readonly_fields = ["external_id"]
    search_fields = ["id"]
    inlines = [user_food_portion.UserFoodPortionAdminInline]


class UserFoodMembershipChildAdminInline(GenericTabularInline):
    """User Food Membership Child Admin Inline"""

    model = UserFoodMembership
    extra = 0
    ct_field = "child_type"
    ct_fk_field = "child_id"
    readonly_fields = ["external_id"]


class UserFoodMembershipParentAdminInline(GenericTabularInline):
    """User Food Membership Parent Admin Inline"""

    model = UserFoodMembership
    extra = 0
    ct_field = "parent_type"
    ct_fk_field = "parent_id"
    readonly_fields = ["external_id"]
