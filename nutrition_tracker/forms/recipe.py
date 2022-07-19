"""Recipe form, process edits to user recipes."""
from __future__ import annotations

from datetime import date
from typing import Any

from django import forms
from django.contrib.contenttypes.forms import BaseGenericInlineFormSet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import users.models as user_model
from nutrition_tracker.forms import base, mixins
from nutrition_tracker.logic import data_loaders
from nutrition_tracker.models import user_recipe


class RecipeForm(forms.Form, mixins.MembersMixin, mixins.ServingsMixin):
    """Recipe form."""

    external_id = forms.UUIDField(widget=forms.HiddenInput(), required=False)
    name = forms.CharField(label=_("Name"))
    recipe_date = forms.DateField(label=_("Recipe date"), required=False)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.user: user_model.User = kwargs.pop("user")
        self.lrecipe: user_recipe.UserRecipe = kwargs.pop("lrecipe", None)

        super().__init__(*args, **kwargs)
        self._init_details()
        self.helper: base.RecipeFormHelper = base.RecipeFormHelper(self)

    def _init_details(self) -> None:
        """Initialize food metadata in form."""
        if self.lrecipe:
            self.fields["external_id"].initial = self.lrecipe.external_id
            self.fields["name"].initial = self.lrecipe.name
            self.fields["recipe_date"].initial = self.lrecipe.recipe_date
        else:
            self.fields["recipe_date"].initial = timezone.localdate()

    def save(
        self,
        servings: BaseGenericInlineFormSet,
        food_members: BaseGenericInlineFormSet,
        recipe_members: BaseGenericInlineFormSet,
    ) -> user_recipe.UserRecipe:
        """Save form."""
        self._save_details()
        self._save_servings(servings, self.lrecipe, data_loaders.get_content_type_recipe())
        self._save_members(food_members, self.lrecipe, data_loaders.get_content_type_ingredient())
        self._save_members(recipe_members, self.lrecipe, data_loaders.get_content_type_recipe())
        return self.lrecipe

    def _save_details(self) -> None:
        """Save recipe metadata in form."""
        name: str = self.cleaned_data["name"]
        recipe_date: date | None = self.cleaned_data["recipe_date"]
        if self.lrecipe:
            if "name" in self.changed_data or "recipe_date" in self.changed_data:
                self.lrecipe.name = name
                self.lrecipe.recipe_date = recipe_date
                self.lrecipe.save()
        else:
            self.lrecipe = user_recipe.create(self.user, name=name, recipe_date=recipe_date)
