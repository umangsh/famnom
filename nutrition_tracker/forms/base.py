"""Form layout helpers for crispy forms."""
from __future__ import annotations

import re
import uuid
from typing import Any, Sequence

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django.contrib.contenttypes.forms import BaseGenericInlineFormSet

import users.models as user_model
from nutrition_tracker.forms import layout


class FormHelperBase(FormHelper):
    """Base formhelper class for form layouts."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.form_class: str = "form-horizontal"
        self.form_method: str = "post"
        self.label_class: str = "col-lg-4 text-lg-right font-weight-bold pl-0"
        self.field_class: str = "col-lg-8 pl-0"


class FormsetHelperBase(FormHelperBase):
    """Base formhelper class for formset layouts."""

    def __init__(self, formset: BaseGenericInlineFormSet, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.formset_prefix: str = re.sub("-[0-9]+$", "", formset.prefix)
        self.form_tag: bool = False
        self.disable_csrf: bool = True


class FoodFormHelper(FormHelperBase):
    """Food form layout helper"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.layout: Layout = layout.food()


class RecipeFormHelper(FormHelperBase):
    """Recipe form layout helper"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.layout: Layout = layout.recipe()


class MealFormHelper(FormHelperBase):
    """Meal form layout helper"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.layout: Layout = layout.meal()


class LogFormHelper(FormHelperBase):
    """Log form layout helper"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.layout: Layout = layout.log()


class NutritionFormHelper(FormHelperBase):
    """Nutrition form layout helper"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.label_class: str = "col-lg-3 text-lg-right font-weight-bold pl-0"
        self.field_class: str = "col-lg-6 pl-0 threshold-value"
        self.layout: Layout = layout.nutrition()


class ProfileFormHelper(FormHelperBase):
    """Profile form layout helper"""

    def __init__(self, family_members: list[user_model.User], *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.label_class: str = "col-lg-3 text-lg-right font-weight-bold pl-0"
        self.field_class: str = "col-lg-6 pl-0"
        self.layout: Layout = layout.profile(family_members)


class MealplanFormHelper(FormHelperBase):
    """Mealplan base form layout helper"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.label_class: str = "col-lg-0 px-0"
        self.field_class: str = "col-lg-12 pl-0"


class MealplanFormOneHelper(MealplanFormHelper):
    """Mealplan form one layout helper"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.layout: Layout = layout.mealplan_one()


class MealplanFormTwoHelper(MealplanFormHelper):
    """Mealplan form two layout helper"""

    def __init__(self, rows: Sequence[str | uuid.UUID], *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.label_class: str = "col-lg-6 text-lg-right pl-0"
        self.field_class: str = "col-lg-3 pl-0 threshold-value"
        self.layout: Layout = layout.mealplan_two(rows)


class MealplanFormThreeHelper(MealplanFormHelper):
    """Mealplan form three layout helper"""

    def __init__(self, rows: Sequence[str | uuid.UUID], *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.label_class: str = "col-lg-12 px-0"
        self.field_class: str = "col-lg-12 px-0"
        self.layout: Layout = layout.mealplan_three(rows)


class CreateFoodMemberFormsetHelper(FormsetHelperBase):
    """Create food member formset layout helper"""

    def __init__(self, formset: BaseGenericInlineFormSet, *args: Any, **kwargs: Any) -> None:
        super().__init__(formset, *args, **kwargs)
        self.layout: Layout = layout.create_food_member(self.formset_prefix)


class EditFoodMemberFormsetHelper(FormsetHelperBase):
    """Edit food member formset layout helper"""

    def __init__(self, formset: BaseGenericInlineFormSet, *args: Any, **kwargs: Any) -> None:
        super().__init__(formset, *args, **kwargs)
        self.layout: Layout = layout.edit_food_member(self.formset_prefix)


class CreateRecipeMemberFormsetHelper(FormsetHelperBase):
    """Create recipe member formset layout helper"""

    def __init__(self, formset: BaseGenericInlineFormSet, *args: Any, **kwargs: Any) -> None:
        super().__init__(formset, *args, **kwargs)
        self.layout: Layout = layout.create_recipe_member(self.formset_prefix)


class EditRecipeMemberFormsetHelper(FormsetHelperBase):
    """Edit recipe member formset layout helper"""

    def __init__(self, formset: BaseGenericInlineFormSet, *args: Any, **kwargs: Any) -> None:
        super().__init__(formset, *args, **kwargs)
        self.layout: Layout = layout.edit_recipe_member(self.formset_prefix)


class FoodPortionFormsetHelper(FormsetHelperBase):
    """Food portion formset layout helper"""

    def __init__(self, formset: BaseGenericInlineFormSet, *args: Any, **kwargs: Any) -> None:
        minimal: bool = kwargs.pop("minimal", False)
        super().__init__(formset, *args, **kwargs)
        self.layout: Layout = layout.food_portion(self.formset_prefix, minimal=minimal)


class FoodPortionRecipeFormsetHelper(FoodPortionFormsetHelper):
    """Recipe portion formset layout helper"""

    def __init__(self, formset: BaseGenericInlineFormSet, *args: Any, **kwargs: Any) -> None:
        super().__init__(formset, *args, minimal=True, **kwargs)
