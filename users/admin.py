# pylint: skip-file
"""User admin module."""
from __future__ import annotations

from bitfield import BitField
from bitfield.forms import BitFieldCheckboxSelectMultiple
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import User


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "date_of_birth", "flags")

    def clean_password2(self) -> str:
        """Check that the two password entries match"""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit: bool = True) -> User:
        """Save the provided password in hashed format"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "password",
            "date_of_birth",
            "flags",
            "is_active",
            "is_staff",
        )

    def clean_password(self) -> str:
        """Regardless of what the user provides, return the initial value. This is done here, rather than on the field, because the field does not have access to the initial value"""
        return self.initial["password"]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    formfield_overrides = {
        BitField: {"widget": BitFieldCheckboxSelectMultiple},
    }

    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = (
        "external_id",
        "email",
        "first_name",
        "last_name",
        "date_of_birth",
        "family_id",
        "family_added_timestamp",
        "is_staff",
    )
    list_filter = ("is_staff", "is_active")
    fieldsets = (
        (None, {"fields": ("external_id", "email", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "date_of_birth",
                    "flags",
                    "family_id",
                    "family_added_timestamp",
                    "is_active",
                )
            },
        ),
        ("Permissions", {"fields": ("is_staff",)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("first_name", "last_name", "email", "date_of_birth", "flags", "password1", "password2"),
            },
        ),
    )
    readonly_fields = ("external_id",)
    search_fields = ("email",)
    ordering = ("email",)
    filter_horizontal = ()
