"""Food form, process edits to user foods/ingredients."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from django import forms
from django.conf import settings
from django.contrib.contenttypes.forms import BaseGenericInlineFormSet
from django.utils.translation import gettext_lazy as _

import users.models as user_model
from nutrition_tracker.constants import constants
from nutrition_tracker.forms import base, mixins
from nutrition_tracker.logic import data_loaders, food_category, food_nutrient
from nutrition_tracker.logic import forms as forms_logic
from nutrition_tracker.logic import search_indexing
from nutrition_tracker.models import (
    db_branded_food,
    db_food,
    db_food_nutrient,
    search_result,
    user_branded_food,
    user_food_nutrient,
    user_ingredient,
)
from nutrition_tracker.utils import form as form_utils


class FoodForm(forms.Form, mixins.ServingsMixin):
    """Food form."""

    external_id = forms.UUIDField(widget=forms.HiddenInput(), required=False)
    name = forms.CharField(label=_("Name"), max_length=1000, required=False)
    brand_name = forms.CharField(label=_("Brand name"), max_length=1000, required=False)
    subbrand_name = forms.CharField(label=_("Subbrand name"), max_length=1000, required=False)
    brand_owner = forms.CharField(label=_("Brand owner"), max_length=1000, required=False)
    gtin_upc = forms.CharField(label=_("GTIN/UPC"), max_length=20, required=False)
    category_id = forms.ChoiceField(label=_("Category"), required=False, choices=food_category.for_display_choices())

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.user: user_model.User = kwargs.pop("user")
        self.lfood: user_ingredient.UserIngredient = kwargs.pop("lfood", None)
        self.food_portions: list[tuple[UUID, str, float | None, str | None, float | None, float | None]] = kwargs.pop(
            "food_portions", []
        )
        self.food_nutrients: list[db_food_nutrient.DBFoodNutrient | user_food_nutrient.UserFoodNutrient] = kwargs.pop(
            "food_nutrients", []
        )
        self.serving_size: float | None = None
        self.serving_size_unit: str | None = None

        super().__init__(*args, **kwargs)
        self._init_details()
        self._init_nutrients()
        self.helper: base.FoodFormHelper = base.FoodFormHelper(self)

    def _init_details(self) -> None:
        """Initialize food metadata in form."""
        if self.lfood:
            self.fields["external_id"].initial = self.lfood.external_id
            self.fields["name"].initial = self.lfood.name
            self.fields["category_id"].initial = self.lfood.category_id

        if self.lfood and self.lfood.branded_foods:  # type: ignore
            for field in constants.BRAND_FIELDS:
                self.fields[field].initial = getattr(self.lfood.branded_foods[0], field)  # type: ignore

        if self.lfood and self.lfood.db_food:
            cfood: db_food.DBFood = self.lfood.db_food
            self.fields["name"].help_text = _("From Food database: %(name)s") % {"name": cfood.display_name}

            for field in constants.BRAND_FIELDS:
                field_value: str | None = cfood.display_brand_field(field)
                if field_value:
                    self.fields[field].help_text = _("From Food database: %(value)s") % {"value": field_value}

            if cfood.food_category_id:
                self.fields["category_id"].help_text = _("From Food database: %(name)s") % {
                    "name": food_category.for_display(cfood.food_category_id)
                }

    def _init_servings(self) -> None:
        """Initialize food portions in form."""
        if self.food_portions:
            self.serving_size = self.food_portions[0][2]
            self.serving_size_unit = self.food_portions[0][3]

    def _init_nutrients(self) -> None:
        """Initialize food nutrients in form."""
        for nutrient_id in constants.FORM_NUTRIENT_IDS:
            is_required: bool = nutrient_id in constants.FORM_REQUIRED_NUTRIENT_IDS
            self.fields[form_utils.get_field_name(nutrient_id)] = forms.FloatField(
                label=f"{food_nutrient.for_display(nutrient_id)} ({food_nutrient.for_display_unit(nutrient_id)})",
                min_value=0,
                required=is_required,
            )

            if self.food_nutrients:
                nutrient_amount: float | None = food_nutrient.get_nutrient_amount(self.food_nutrients, nutrient_id)

                if not nutrient_amount:
                    continue

                if self.food_portions and self.food_portions[0][2]:
                    serving_size: float = self.food_portions[0][2]
                else:
                    serving_size = constants.PORTION_SIZE

                self.fields[form_utils.get_field_name(nutrient_id)].initial = round(
                    nutrient_amount * serving_size / constants.PORTION_SIZE, constants.RW_FLOAT_PRECISION
                )

    def save(self, servings: BaseGenericInlineFormSet) -> user_ingredient.UserIngredient:
        """Save form."""
        is_new_lfood: bool = not self.lfood
        self._save_details(is_new_lfood)
        self._save_servings(
            servings, self.lfood, data_loaders.get_content_type_ingredient(), is_new_lfood=is_new_lfood
        )
        self._save_nutrients(is_new_lfood)
        return self.lfood

    def _save_details(self, is_new_lfood: bool) -> None:
        """Save food metadata in form."""
        name: str | None = self.cleaned_data["name"]
        # Empty category_ids are '', cast them to None
        category_id: int | None = self.cleaned_data["category_id"] or None
        brand_name: str | None = self.cleaned_data["brand_name"]
        subbrand_name: str | None = self.cleaned_data["subbrand_name"]
        brand_owner: str | None = self.cleaned_data["brand_owner"]
        gtin_upc: str | None = self.cleaned_data["gtin_upc"]

        if is_new_lfood:
            self.lfood = user_ingredient.create(self.user)
            cfood: db_food.DBFood = db_food.create(
                source_id=self.lfood.id,
                source_type=constants.DBFoodSourceType.USER,
                description=name,
                food_category_id=category_id,
            )
            self.lfood.db_food = cfood
            self.lfood.save()

            if any(field for field in constants.BRAND_FIELDS if field in self.changed_data):
                db_branded_food.create(
                    db_food=cfood,
                    brand_owner=brand_owner,
                    brand_name=brand_name,
                    subbrand_name=subbrand_name,
                    gtin_upc=gtin_upc,
                )

            return

        if "name" in self.changed_data:
            self.lfood.name = name

        if "category_id" in self.changed_data:
            self.lfood.category_id = category_id

        if "name" in self.changed_data or "category_id" in self.changed_data:
            self.lfood.save()

        if self.lfood.user and any(field for field in constants.BRAND_FIELDS if field in self.changed_data):
            user_branded_food.update_or_create(
                self.lfood.user,
                ingredient=self.lfood,
                defaults={
                    "brand_name": brand_name,
                    "subbrand_name": subbrand_name,
                    "brand_owner": brand_owner,
                    "gtin_upc": gtin_upc,
                },
            )

    def _save_nutrients(self, is_new_lfood: bool) -> None:
        """Save food nutrients in form."""
        if not self.lfood.user:
            return

        lfood: user_ingredient.UserIngredient | None = user_ingredient.load_lfood(self.lfood.user, id_=self.lfood.id)
        if not lfood:
            return

        self.lfood = lfood
        if not self.lfood.user:
            return

        serving_size, _unused = forms_logic.get_serving_defaults(self.lfood)
        for nutrient_id in constants.FORM_NUTRIENT_IDS:
            field_name: str = form_utils.get_field_name(nutrient_id)
            if field_name not in self.changed_data:
                continue

            amount: float | None = self.cleaned_data[form_utils.get_field_name(nutrient_id)]
            if amount is not None:
                if is_new_lfood:
                    db_food_nutrient.create(
                        db_food=self.lfood.db_food,
                        source_type=constants.DBFoodSourceType.USER,
                        nutrient_id=nutrient_id,
                        amount=amount * constants.PORTION_SIZE / serving_size,
                    )
                else:
                    user_food_nutrient.update_or_create(
                        self.lfood.user,
                        ingredient=self.lfood,
                        nutrient_id=nutrient_id,
                        defaults={
                            "amount": amount * constants.PORTION_SIZE / serving_size,
                        },
                    )
