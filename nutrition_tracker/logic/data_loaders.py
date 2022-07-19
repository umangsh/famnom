"""Data loading logic module. Batch load APIs for foods/recipes in recipes/meals."""
from __future__ import annotations

from typing import Sequence, TypeVar

from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet

import users.models as user_model
from nutrition_tracker.models import user_base, user_food_membership, user_ingredient, user_meal, user_recipe


def get_lfood_ids_for_lparents(
    user: user_model.User, lparents: Sequence[user_recipe.UserRecipe] | Sequence[user_meal.UserMeal]
) -> set[int]:
    """Get all food ids in a list of parents - recipes/meals."""
    lfood_ids: set[int] = set()
    if not lparents:
        return lfood_ids

    lrecipe_ids: set[int] = set()
    for lparent in lparents:
        for lmember in lparent.members:  # type: ignore
            if lmember.child_type_id == get_content_type_ingredient_id():
                lfood_ids.add(lmember.child_id)
            elif lmember.child_type_id == get_content_type_recipe_id():
                lrecipe_ids.add(lmember.child_id)

    lrecipes: Sequence[user_recipe.UserRecipe] = (
        list(user_recipe.load_lrecipes(user, ids=list(lrecipe_ids))) if lrecipe_ids else []
    )
    lfood_ids.update(get_lfood_ids_for_lparents(user, lrecipes))
    return lfood_ids


def load_lfoods_for_lparents(
    user: user_model.User, lparents: Sequence[user_recipe.UserRecipe] | Sequence[user_meal.UserMeal]
) -> QuerySet[user_ingredient.UserIngredient]:
    """Get all foods (user_ingredient) objects in a list of parents - recipes/meals."""
    if not lparents:
        return user_ingredient.empty_qs()

    lfood_ids: set[int] = get_lfood_ids_for_lparents(user, lparents)
    if not lfood_ids:
        return user_ingredient.empty_qs()

    return user_ingredient.load_lfoods(user, ids=list(lfood_ids))


def get_lrecipe_ids_for_lparents(
    user: user_model.User, lparents: Sequence[user_recipe.UserRecipe] | Sequence[user_meal.UserMeal]
) -> set[int]:
    """Get all recipe ids in a list of parents - recipes/meals."""
    lrecipe_ids: set[int] = set()
    if not lparents:
        return lrecipe_ids

    for lparent in lparents:
        for lmember in lparent.members:  # type: ignore
            if lmember.child_type_id == get_content_type_recipe_id():
                lrecipe_ids.add(lmember.child_id)

    lrecipes: Sequence[user_recipe.UserRecipe] = (
        list(user_recipe.load_lrecipes(user, ids=list(lrecipe_ids))) if lrecipe_ids else []
    )
    lrecipe_ids.update(get_lrecipe_ids_for_lparents(user, lrecipes))
    return lrecipe_ids


def load_lrecipes_for_lparents(
    user: user_model.User, lparents: Sequence[user_recipe.UserRecipe] | Sequence[user_meal.UserMeal]
) -> QuerySet[user_recipe.UserRecipe]:
    """Get all recipe objects in a list of parents - recipes/meals."""
    if not lparents:
        return user_recipe.empty_qs()

    lrecipe_ids: set[int] = get_lrecipe_ids_for_lparents(user, lparents)
    if not lrecipe_ids:
        return user_recipe.empty_qs()

    return user_recipe.load_lrecipes(user, ids=list(lrecipe_ids))


TUserBase = TypeVar("TUserBase", bound=user_base.UserBase)


def get_content_type(cls: type[TUserBase]) -> ContentType:
    """Get content type."""
    return ContentType.objects.get_for_model(cls)


def get_content_type_id(cls: type[TUserBase]) -> int:
    """Get content type ID."""
    return get_content_type(cls).id


def get_content_type_ingredient() -> ContentType:
    """Get user_ingredient content type."""
    return get_content_type(user_ingredient.UserIngredient)


def get_content_type_ingredient_id() -> int:
    """Get user_ingredient content type ID."""
    return get_content_type_id(user_ingredient.UserIngredient)


def get_content_type_recipe() -> ContentType:
    """Get user_recipe content type."""
    return get_content_type(user_recipe.UserRecipe)


def get_content_type_recipe_id() -> int:
    """Get user_recipe content type ID."""
    return get_content_type_id(user_recipe.UserRecipe)


def get_content_type_meal() -> ContentType:
    """Get user_meal content type."""
    return get_content_type(user_meal.UserMeal)


def get_content_type_meal_id() -> int:
    """Get user_meal content type ID."""
    return get_content_type_id(user_meal.UserMeal)


def get_content_type_membership() -> ContentType:
    """Get membership content type."""
    return get_content_type(user_food_membership.UserFoodMembership)


def get_content_type_membership_id() -> int:
    """Get membership content type ID."""
    return get_content_type_id(user_food_membership.UserFoodMembership)
