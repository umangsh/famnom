"""User profile form module."""
from __future__ import annotations

from datetime import date
from typing import Any

from django import forms
from django.utils.translation import gettext_lazy as _

import users.models as user_model
from nutrition_tracker.biz import user
from nutrition_tracker.forms import base


class ProfileForm(forms.Form):
    """Profile edits form."""

    first_name = forms.CharField(label=_("First Name"), max_length=150, required=False)
    last_name = forms.CharField(label=_("Last Name"), max_length=150, required=False)
    email = forms.EmailField(label=_("Email Address"))
    date_of_birth = forms.DateField(label=_("Date of Birth"), required=False)
    is_pregnant = forms.BooleanField(label=_("Pregnant"), widget=forms.CheckboxInput(), required=False)
    family_email = forms.EmailField(label=_("Add to Family (by email)"), required=False)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.user: user_model.User = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self._init_details()

    def _init_details(self) -> None:
        """Initialize profile metadata in form."""
        self.fields["first_name"].initial = self.user.first_name
        self.fields["last_name"].initial = self.user.last_name
        self.fields["email"].initial = self.user.email
        self.fields["date_of_birth"].initial = self.user.date_of_birth
        self.fields["is_pregnant"].initial = self.user.is_pregnant()
        self.helper: base.ProfileFormHelper = base.ProfileFormHelper(list(user.get_family_members(self.user)), self)

    def save(self) -> None:
        """Save form."""
        self._save_details()

    def _save_details(self) -> None:
        """Save profile metadata in form."""
        if not self.changed_data:
            return

        if not self.user:
            return

        first_name: str | None = self.cleaned_data["first_name"]
        last_name: str | None = self.cleaned_data["last_name"]
        email: str | None = self.cleaned_data["email"]
        date_of_birth: date | None = self.cleaned_data["date_of_birth"]
        is_pregnant: bool | None = self.cleaned_data["is_pregnant"]
        family_email: str | None = self.cleaned_data["family_email"]
        if "first_name" in self.changed_data and first_name:
            self.user.first_name = first_name

        if "last_name" in self.changed_data and last_name:
            self.user.last_name = last_name

        if "email" in self.changed_data and email:
            self.user.add_email(email)
            self.user.email = email

        if "date_of_birth" in self.changed_data:
            self.user.date_of_birth = date_of_birth

        if "is_pregnant" in self.changed_data and is_pregnant is not None:
            self.user.update_flag(user_model.User.FLAG_IS_PREGNANT, is_pregnant)

        if "family_email" in self.changed_data and family_email:
            user.create_family(self.user, family_email)

        self.user.save()
