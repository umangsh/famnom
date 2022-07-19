"""Views mixins module - loads data objects."""
from __future__ import annotations

from typing import Any
from uuid import UUID

import users.models as user_model
from nutrition_tracker.constants import constants
from nutrition_tracker.logic import data_loaders, food_nutrient, food_portion, user_prefs
from nutrition_tracker.models import (
    db_food,
    user_food_membership,
    user_ingredient,
    user_meal,
    user_preference,
    user_recipe,
)


class ObjectMixin:
    """Base object mixin."""

    MESSAGE_INVALID_ID: str = constants.MESSAGE_ERROR_INVALID_ID
    MESSAGE_UNSUPPORTED_ACTION: str = constants.MESSAGE_ERROR_UNSUPPORTED_ACTION

    def __init__(self) -> None:
        self.lobject: None | (
            db_food.DBFood | user_ingredient.UserIngredient | user_recipe.UserRecipe | user_meal.UserMeal
        ) = None

    def load_data(self) -> None:
        """Load extra data."""
        self.nutrient_preferences: list[user_preference.UserPreference] = list(
            user_prefs.load_nutrition_preferences(self.request.user)  # type: ignore
        )

    def get_context_data(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Add additional data to context."""
        context: dict[str, Any] = super().get_context_data(*args, **kwargs)  # type: ignore
        context.setdefault("lfood", getattr(self, "lfood", None))
        context.setdefault("cfood", getattr(self, "cfood", None))
        context.setdefault("lrecipe", getattr(self, "lrecipe", None))
        context.setdefault("lmeal", getattr(self, "lmeal", None))
        context.setdefault("lfoods", getattr(self, "lfoods", []))
        context.setdefault("member_recipes", getattr(self, "member_recipes", []))
        context.setdefault("lmeals", getattr(self, "lmeals", []))
        context.setdefault("food_nutrients", getattr(self, "food_nutrients", []))
        context.setdefault("food_portions", getattr(self, "food_portions", []))
        context.setdefault("nutrient_preferences", getattr(self, "nutrient_preferences", []))
        return context


class FoodMixin(ObjectMixin):
    """DBFood mixin."""

    MESSAGE_LOG_SUCCESS: str = constants.MESSAGE_SUCCESS_FOOD_LOG
    MESSAGE_OBJECT_NOT_FOUND: str = constants.MESSAGE_ERROR_MISSING_FOOD
    URL_INVALID_ID: str = constants.URL_SEARCH
    URL_LOG_SUCCESS: str = constants.URL_HOME
    URL_OBJECT_NOT_FOUND: str = constants.URL_SEARCH

    def load_object(self, **kwargs: Any) -> None:
        """Load object."""
        self.external_id = kwargs.get("id")
        self.lobject = db_food.load_cfood(external_id=self.external_id)

    def load_data(self) -> None:
        """Load extra data."""
        if not self.lobject:
            return super().load_data()

        luser: user_model.User = self.request.user  # type: ignore
        self.cfood = self.lobject
        self.lfood = user_ingredient.load_lfood(luser, db_food_id=self.cfood.id)
        self.food_nutrients = food_nutrient.get_food_nutrients(self.lfood, self.cfood)  # type: ignore
        self.food_portions: list[
            tuple[UUID, str, float | None, str | None, float | None, float | None]
        ] = food_portion.for_display_choices(
            self.lfood, cfood=self.cfood  # type: ignore
        )
        return super().load_data()

    def get_context_data(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(*args, **kwargs)
        if not hasattr(self, "food_portions"):
            return context

        context["default_portion"] = self.food_portions[0]
        return context


class IngredientMixin(ObjectMixin):  # pylint: disable=too-many-instance-attributes
    """UserIngredient mixin."""

    MESSAGE_LOG_SUCCESS: str = constants.MESSAGE_SUCCESS_FOOD_LOG
    MESSAGE_OBJECT_NOT_FOUND: str = constants.MESSAGE_ERROR_MISSING_FOOD
    MESSAGE_SUCCESS: str = constants.MESSAGE_SUCCESS_FOOD_SAVE
    URL_INVALID_ID: str = constants.URL_MY_FOODS
    URL_INVALID_SEARCH: str = constants.URL_MY_FOODS
    URL_LOG_SUCCESS: str = constants.URL_HOME
    URL_NOT_ALLOWED: str = constants.URL_MY_FOODS
    URL_OBJECT_NOT_FOUND: str = constants.URL_MY_FOODS
    URL_SUCCESS: str = constants.URL_DETAIL_INGREDIENT

    def load_object(self, **kwargs: Any) -> None:
        """Load object."""
        self.external_id = kwargs.get("id")
        luser: user_model.User = self.request.user  # type: ignore
        self.lobject = user_ingredient.load_lfood(luser, external_id=self.external_id)

        mid = kwargs.get("mid")
        self.lmembership = user_food_membership.load_lmembership(luser, external_id=mid)

    def load_data(self) -> None:
        """Load extra data."""
        if not self.lobject:
            return super().load_data()

        self.lfood = self.lobject
        self.cfood = self.lfood.db_food  # type: ignore
        self.food_nutrients = food_nutrient.get_food_nutrients(self.lfood, self.cfood)  # type: ignore
        self.food_portions: list[
            tuple[UUID, str, float | None, str | None, float | None, float | None]
        ] = food_portion.for_display_choices(
            self.lfood, cfood=self.cfood  # type: ignore
        )
        if self.lmembership:
            self.lmeal = self.lmembership.parent

        return super().load_data()

    def get_context_data(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(*args, **kwargs)
        if not hasattr(self, "food_portions"):
            return context

        context["default_portion"] = self.food_portions[0]
        if self.lmembership:
            portion = food_portion.get_food_member_portion(self.lmembership.portions[0], self.food_portions)  # type: ignore
            if portion:
                default_portion, quantity = portion
                context["default_portion"] = default_portion
                context["default_portion_quantity"] = quantity
        return context


class RecipeMixin(ObjectMixin):  # pylint: disable=too-many-instance-attributes
    """UserRecipe mixin."""

    MESSAGE_LOG_SUCCESS: str = constants.MESSAGE_SUCCESS_RECIPE_LOG
    MESSAGE_OBJECT_NOT_FOUND: str = constants.MESSAGE_ERROR_MISSING_RECIPE
    MESSAGE_SUCCESS: str = constants.MESSAGE_SUCCESS_RECIPE_SAVE
    URL_INVALID_ID: str = constants.URL_MY_RECIPES
    URL_INVALID_SEARCH: str = constants.URL_MY_RECIPES
    URL_LOG_SUCCESS: str = constants.URL_HOME
    URL_NOT_ALLOWED: str = constants.URL_MY_RECIPES
    URL_OBJECT_NOT_FOUND: str = constants.URL_MY_RECIPES
    URL_SUCCESS: str = constants.URL_DETAIL_RECIPE

    def load_object(self, **kwargs: Any) -> None:
        """Load object."""
        self.external_id = kwargs.get("id")
        luser: user_model.User = self.request.user  # type: ignore
        self.lobject = user_recipe.load_lrecipe(luser, external_id=self.external_id)

        mid = kwargs.get("mid")
        self.lmembership = user_food_membership.load_lmembership(luser, external_id=mid)

    def load_data(self) -> None:
        """Load extra data."""
        if not self.lobject:
            return super().load_data()

        luser: user_model.User = self.request.user  # type: ignore
        self.lrecipe = self.lobject
        self.lfoods = list(data_loaders.load_lfoods_for_lparents(luser, [self.lrecipe]))  # type: ignore
        self.member_recipes = list(data_loaders.load_lrecipes_for_lparents(luser, [self.lrecipe]))  # type: ignore
        self.food_nutrients = food_nutrient.get_foods_nutrients(luser, self.lfoods)
        self.food_portions: list[
            tuple[UUID, str, float | None, str | None, float | None, float | None]
        ] = food_portion.for_display_choices(
            self.lrecipe  # type: ignore
        )
        if self.lmembership:
            self.lmeal = self.lmembership.parent

        return super().load_data()

    def get_context_data(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(*args, **kwargs)
        if not hasattr(self, "food_portions"):
            return context

        context["default_portion"] = self.food_portions[0]
        if self.lmembership:
            portion = food_portion.get_food_member_portion(self.lmembership.portions[0], self.food_portions)  # type: ignore
            if portion:
                default_portion, quantity = portion
                context["default_portion"] = default_portion
                context["default_portion_quantity"] = quantity
        return context


class MealMixin(ObjectMixin):
    """UserMeal mixin."""

    MESSAGE_OBJECT_NOT_FOUND: str = constants.MESSAGE_ERROR_MISSING_MEAL
    MESSAGE_SUCCESS: str = constants.MESSAGE_SUCCESS_MEAL_SAVE
    URL_INVALID_ID: str = constants.URL_MY_MEALS
    URL_INVALID_SEARCH: str = constants.URL_MY_MEALS
    URL_NOT_ALLOWED: str = constants.URL_MY_MEALS
    URL_OBJECT_NOT_FOUND: str = constants.URL_MY_MEALS
    URL_SUCCESS: str = constants.URL_DETAIL_MEAL

    def load_object(self, **kwargs: Any) -> None:
        """Load object."""
        self.external_id = kwargs.get("id")
        luser: user_model.User = self.request.user  # type: ignore
        self.lobject = user_meal.load_lmeal(luser, external_id=self.external_id)

    def load_data(self) -> None:
        """Load extra data."""
        if not self.lobject:
            return super().load_data()

        luser: user_model.User = self.request.user  # type: ignore
        self.lmeal = self.lobject
        self.lfoods = list(data_loaders.load_lfoods_for_lparents(luser, [self.lmeal]))  # type: ignore
        self.member_recipes = list(data_loaders.load_lrecipes_for_lparents(luser, [self.lmeal]))  # type: ignore
        self.food_nutrients = food_nutrient.get_foods_nutrients(luser, self.lfoods)
        return super().load_data()
