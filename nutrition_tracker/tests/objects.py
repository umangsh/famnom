"""Test objects used by python tests."""
from __future__ import annotations

import datetime
from typing import Any

from allauth.account.models import EmailAddress
from allauth.utils import get_user_model
from django.utils import timezone
from rest_framework_api_key.models import APIKey

import users.models as user_model
from nutrition_tracker.config import usda_config
from nutrition_tracker.constants import constants
from nutrition_tracker.logic import food_category, search_indexing
from nutrition_tracker.models import (
    db_branded_food,
    db_food,
    db_food_nutrient,
    db_food_portion,
    search_result,
    usda_branded_food,
    usda_fndds_food,
    usda_food,
    usda_food_nutrient,
    usda_food_portion,
    usda_foundation_food,
    usda_sr_legacy,
    user_branded_food,
    user_food_membership,
    user_food_nutrient,
    user_food_portion,
    user_ingredient,
    user_meal,
    user_preference,
    user_preference_threshold,
    user_recipe,
)
from nutrition_tracker.tests import constants as test_constants


#
# USDA objects
#
def get_usda_food() -> usda_food.USDAFood:
    """Get USDA Food."""
    cfood, _unused = usda_food.get_or_create(fdc_id=1)
    cfood.description = "test"
    cfood.data_type = constants.USDA_BRANDED_FOOD
    cfood.save()
    return cfood


def get_usda_food_2() -> usda_food.USDAFood:
    """Get USDA Food 2."""
    cfood, _unused = usda_food.get_or_create(fdc_id=2, description="test_2")
    return cfood


def get_usda_food_unknown_type() -> usda_food.USDAFood:
    """Get USDA Food with unknown data_type."""
    cfood, _unused = usda_food.get_or_create(fdc_id=3, description="test_2", data_type="unknown")
    return cfood


def get_usda_branded_food() -> usda_branded_food.USDABrandedFood:
    """Get USDA Branded Food for USDA Food."""
    cfood: usda_food.USDAFood = get_usda_food()
    return usda_branded_food.create(
        usda_food=cfood,
        brand_name="brand",
        brand_owner="owner",
        gtin_upc="usda_upc",
        serving_size=50,
        serving_size_unit="g",
        household_serving_fulltext="4 cups",
    )


def get_usda_fndds_food() -> usda_fndds_food.USDAFnddsFood:
    """Get USDA Fndds Food."""
    cfood: usda_food.USDAFood = get_usda_food()
    return usda_fndds_food.create(usda_food=cfood, food_code=1)


def get_usda_foundation_food() -> usda_foundation_food.USDAFoundationFood:
    """Get USDA Foundation Food."""
    cfood: usda_food.USDAFood = get_usda_food()
    return usda_foundation_food.create(usda_food=cfood, ndb_number="123")


def get_usda_sr_legacy_food() -> usda_sr_legacy.USDASRLegacy:
    """Get USDA SR Legacy Food."""
    cfood: usda_food.USDAFood = get_usda_food()
    return usda_sr_legacy.create(usda_food=cfood, ndb_number="123")


def get_usda_food_portion() -> usda_food_portion.USDAFoodPortion:
    """Get USDA Food Portion."""
    cfood: usda_food.USDAFood = get_usda_food()
    return usda_food_portion.create(id=1, usda_food=cfood, gram_weight=100)


def get_usda_food_portion_2() -> usda_food_portion.USDAFoodPortion:
    """Get USDA Food Portion."""
    cfood: usda_food.USDAFood = get_usda_food_2()
    return usda_food_portion.create(id=5, usda_food=cfood, gram_weight=147)


def get_usda_food_nutrient() -> usda_food_nutrient.USDAFoodNutrient:
    """Get USDA Food Nutrient."""
    cfood: usda_food.USDAFood = get_usda_food()
    return usda_food_nutrient.create(id=1, usda_food=cfood, nutrient_id=constants.ENERGY_NUTRIENT_ID, amount=100)


def get_usda_food_nutrient_2() -> usda_food_nutrient.USDAFoodNutrient:
    """Get USDA Food Nutrient 2."""
    cfood: usda_food.USDAFood = get_usda_food()
    return usda_food_nutrient.create(id=2, usda_food=cfood, nutrient_id=constants.FAT_NUTRIENT_ID, amount=37)


def get_usda_food_2_nutrient() -> usda_food_nutrient.USDAFoodNutrient:
    """Get USDA Food Nutrient for USDA Food 2."""
    cfood: usda_food.USDAFood = get_usda_food_2()
    return usda_food_nutrient.create(id=3, usda_food=cfood, nutrient_id=constants.ENERGY_NUTRIENT_ID, amount=54)


#
# DB Base objects
#
def get_db_food() -> db_food.DBFood:
    """Get DB Food."""
    cfood, _unused = db_food.get_or_create(id=1)
    cfood.description = "test"
    cfood.source_id = 123
    cfood.source_type = constants.DBFoodSourceType.USDA
    cfood.source_sub_type = constants.DBFoodSourceSubType.USDA_BRANDED_FOOD
    cfood.save()
    return cfood


def get_db_food_2() -> db_food.DBFood:
    """Get DB Food 2."""
    cfood, _unused = db_food.get_or_create(
        id=2,
        description="test_2",
        source_id=234,
        source_type=constants.DBFoodSourceType.USDA,
        source_sub_type=constants.DBFoodSourceSubType.USDA_FOUNDATION_FOOD,
    )
    return cfood


def get_db_branded_food() -> db_branded_food.DBBrandedFood:
    """Get DB Branded Food."""
    cfood: db_food.DBFood = get_db_food()
    return db_branded_food.create(db_food=cfood, brand_name="brand", brand_owner="owner", gtin_upc="db_upc")


def get_db_food_nutrient() -> db_food_nutrient.DBFoodNutrient:
    """Get DB Food Nutrient."""
    cfood: db_food.DBFood = get_db_food()
    return db_food_nutrient.create(id=1, db_food=cfood, nutrient_id=constants.ENERGY_NUTRIENT_ID, amount=100)


def get_db_food_nutrient_2() -> db_food_nutrient.DBFoodNutrient:
    """Get DB Food Nutrient 2."""
    cfood: db_food.DBFood = get_db_food()
    return db_food_nutrient.create(id=2, db_food=cfood, nutrient_id=constants.FAT_NUTRIENT_ID, amount=37)


def get_db_food_portion() -> db_food_portion.DBFoodPortion:
    """Get DB Food Portion."""
    cfood: db_food.DBFood = get_db_food()
    return db_food_portion.create(
        id=1, source_id=12, db_food=cfood, serving_size=100, serving_size_unit=constants.ServingSizeUnit.WEIGHT
    )


def get_db_food_branded_portion() -> db_food_portion.DBFoodPortion:
    """Get DB Food Portion (branded source)."""
    cfood: db_food.DBFood = get_db_food()
    return db_food_portion.create(
        id=4,
        source_id=constants.BRANDED_FOOD_PORTION_ID,
        db_food=cfood,
        serving_size=50,
        serving_size_unit=constants.ServingSizeUnit.WEIGHT,
        portion_description="4 cups",
    )


def get_db_food_portion_2() -> db_food_portion.DBFoodPortion:
    """Get DB Food Portion for DB Food 2."""
    cfood: db_food.DBFood = get_db_food_2()
    return db_food_portion.create(
        id=5, source_id=15, db_food=cfood, serving_size=147, serving_size_unit=constants.ServingSizeUnit.WEIGHT
    )


#
# User objects
#
def get_user() -> user_model.User:
    """Get test user."""
    user, created = get_user_model().objects.get_or_create(
        first_name="Test", last_name="Gupta", email="user@famnom.com", date_of_birth=datetime.date(1988, 2, 2)
    )
    if created:
        user.set_password("password")
        user.save()

    return user


def get_user_2() -> user_model.User:
    """Get test user 2."""
    user, created = get_user_model().objects.get_or_create(
        email="user_2@famnom.com", date_of_birth=datetime.date(1973, 3, 18)
    )
    if created:
        user.set_password("password_2")
        user.save()

    return user


def verify_user(user: user_model.User) -> None:
    """Lookup a user, creating one if necessary in the database, and mark the user as verified."""
    EmailAddress.objects.get_or_create(user=user, email=user.email, primary=True, verified=True)


def get_user_ingredient() -> user_ingredient.UserIngredient:
    """Get user ingredient."""
    user: user_model.User = get_user()
    cfood: db_food.DBFood = get_db_food()
    lfood, _unused = user_ingredient.get_or_create(user, name="test", db_food=cfood, category_id=1)
    return lfood


def get_user_ingredient_2() -> user_ingredient.UserIngredient:
    """Get user ingredient 2."""
    user: user_model.User = get_user()
    cfood: db_food.DBFood = get_db_food_2()
    lfood, _unused = user_ingredient.get_or_create(user, name="test_2", db_food=cfood)
    return lfood


def get_user_2_ingredient() -> user_ingredient.UserIngredient:
    """Get user ingredient for user 2."""
    user: user_model.User = get_user_2()
    cfood: db_food.DBFood = get_db_food_2()
    lfood, _unused = user_ingredient.get_or_create(user, name="test", db_food=cfood)
    return lfood


def get_user_2_ingredient_2() -> user_ingredient.UserIngredient:
    """Get user ingredient 2 for user 2."""
    user: user_model.User = get_user_2()
    lfood, _unused = user_ingredient.get_or_create(user, name="test_ingredient_2")
    return lfood


def get_user_branded_food() -> user_branded_food.UserBrandedFood:
    """Get user branded food for user ingredient."""
    user: user_model.User = get_user()
    lfood: user_ingredient.UserIngredient = get_user_ingredient()
    return user_branded_food.create(
        user, ingredient=lfood, brand_name="brand", brand_owner="owner", gtin_upc="user_upc"
    )


def get_user_2_branded_food() -> user_branded_food.UserBrandedFood:
    """Get user branded food for ingredient 2 for user 2."""
    user: user_model.User = get_user_2()
    lfood: user_ingredient.UserIngredient = get_user_2_ingredient()
    return user_branded_food.create(
        user, ingredient=lfood, brand_name="brand", brand_owner="owner", gtin_upc="user_upc"
    )


def get_recipe() -> user_recipe.UserRecipe:
    """Get Recipe."""
    user: user_model.User = get_user()
    lrecipe, _unused = user_recipe.get_or_create(user, name="Test Recipe", recipe_date=timezone.localdate())
    return lrecipe


def get_recipe_2() -> user_recipe.UserRecipe:
    """Get Recipe 2."""
    user: user_model.User = get_user()
    lrecipe, _unused = user_recipe.get_or_create(user, name="Test Recipe 2", recipe_date=timezone.localdate())
    return lrecipe


def get_user_2_recipe() -> user_recipe.UserRecipe:
    """Get user 2 Recipe."""
    user: user_model.User = get_user_2()
    lrecipe, _unused = user_recipe.get_or_create(user, name="Test Recipe User 2", recipe_date=timezone.localdate())
    return lrecipe


def get_meal_today_1() -> user_meal.UserMeal:
    """Get Meal today 1."""
    user: user_model.User = get_user()
    return user_meal.create(user, meal_date=timezone.localdate(), meal_type=constants.MealType.BREAKFAST)


def get_meal_today_2() -> user_meal.UserMeal:
    """Get Meal today 2."""
    user: user_model.User = get_user()
    return user_meal.create(user, meal_date=timezone.localdate(), meal_type=constants.MealType.LUNCH)


def get_meal_yesterday_1() -> user_meal.UserMeal:
    """Get Meal yesterday 1."""
    user: user_model.User = get_user()
    return user_meal.create(
        user, meal_date=timezone.localdate() - timezone.timedelta(days=1), meal_type=constants.MealType.BREAKFAST
    )


def get_meal_yesterday_2() -> user_meal.UserMeal:
    """Get Meal yesterday 2."""
    user: user_model.User = get_user()
    return user_meal.create(
        user, meal_date=timezone.localdate() - timezone.timedelta(days=1), meal_type=constants.MealType.LUNCH
    )


def get_meal_2_today_1() -> user_meal.UserMeal:
    """Get Meal today 1 for user 2."""
    user: user_model.User = get_user_2()
    return user_meal.create(user, meal_date=timezone.localdate(), meal_type=constants.MealType.BREAKFAST)


def get_category() -> usda_config.USDAFoodCategory | usda_config.WWEIAFoodCategory:
    """Get category for category ID 1."""
    category = food_category.get_category(1)
    assert category is not None
    return category


def get_user_food_membership(parent: Any, child: Any) -> user_food_membership.UserFoodMembership:
    """Get user food membership between parent, child."""
    user: user_model.User = get_user()
    return user_food_membership.create(user, parent=parent, child=child)


def get_user_2_food_membership(parent: Any, child: Any) -> user_food_membership.UserFoodMembership:
    """Get food membership between parent, child for user 2."""
    user: user_model.User = get_user_2()
    return user_food_membership.create(user, parent=parent, child=child)


def get_user_food_nutrient() -> user_food_nutrient.UserFoodNutrient:
    """Get user food nutrient."""
    user: user_model.User = get_user()
    lfood: user_ingredient.UserIngredient = get_user_ingredient()
    return user_food_nutrient.create(user, ingredient=lfood, nutrient_id=constants.ENERGY_NUTRIENT_ID, amount=100)


def get_user_2_food_nutrient() -> user_food_nutrient.UserFoodNutrient:
    """Get user ingredient 2 food nutrient."""
    user: user_model.User = get_user()
    lfood: user_ingredient.UserIngredient = get_user_ingredient_2()
    return user_food_nutrient.create(user, ingredient=lfood, nutrient_id=constants.ENERGY_NUTRIENT_ID, amount=110)


def get_user_food_nutrient_2() -> user_food_nutrient.UserFoodNutrient:
    """Get user food nutrient 2."""
    user: user_model.User = get_user()
    lfood: user_ingredient.UserIngredient = get_user_ingredient()
    return user_food_nutrient.create(user, ingredient=lfood, nutrient_id=constants.PROTEIN_NUTRIENT_ID, amount=54)


def get_user_food_portion() -> user_food_portion.UserFoodPortion:
    """Get user food portion."""
    user: user_model.User = get_user()
    lfood: user_ingredient.UserIngredient = get_user_ingredient()
    return user_food_portion.create(
        user, content_object=lfood, serving_size=83, serving_size_unit=constants.ServingSizeUnit.WEIGHT
    )


def get_user_2_food_portion() -> user_food_portion.UserFoodPortion:
    """Get user ingredient 2 food portion."""
    user: user_model.User = get_user()
    lfood: user_ingredient.UserIngredient = get_user_ingredient_2()
    return user_food_portion.create(
        user, content_object=lfood, serving_size=142, serving_size_unit=constants.ServingSizeUnit.WEIGHT
    )


def get_user_recipe_portion() -> user_food_portion.UserFoodPortion:
    """Get user recipe portion."""
    user: user_model.User = get_user()
    lrecipe: user_recipe.UserRecipe = get_recipe()
    return user_food_portion.create(
        user, content_object=lrecipe, serving_size=200, serving_size_unit=constants.ServingSizeUnit.WEIGHT
    )


def get_user_food_membership_portion(
    ufm: user_food_membership.UserFoodMembership,
) -> user_food_portion.UserFoodPortion:
    """Get user food membership (ufm) portion."""
    user: user_model.User = get_user()
    return user_food_portion.create(
        user, content_object=ufm, serving_size=50, quantity=50, serving_size_unit=constants.ServingSizeUnit.WEIGHT
    )


def get_user_2_food_membership_portion(
    ufm: user_food_membership.UserFoodMembership,
) -> user_food_portion.UserFoodPortion:
    """Get user food membership (ufm) portion for user 2."""
    user: user_model.User = get_user_2()
    return user_food_portion.create(
        user, content_object=ufm, serving_size=50, quantity=50, serving_size_unit=constants.ServingSizeUnit.WEIGHT
    )


def get_user_preference() -> user_preference.UserPreference:
    """Get user preference (with threshold) for user ingredient."""
    user: user_model.User = get_user()
    lfood: user_ingredient.UserIngredient = get_user_ingredient()
    luser_preference: user_preference.UserPreference = user_preference.create(user, food_external_id=lfood.external_id)
    luser_preference.add_flag(user_preference.FLAG_IS_AVAILABLE)
    luser_preference.save()
    user_preference_threshold.create(user, user_preference=luser_preference, num_days=1, min_value=5)
    return luser_preference


def get_user_preference_2() -> user_preference.UserPreference:
    """Get user preference (with threshold) for user ingredient 2."""
    user: user_model.User = get_user()
    lfood: user_ingredient.UserIngredient = get_user_ingredient_2()
    luser_preference: user_preference.UserPreference = user_preference.create(user, food_external_id=lfood.external_id)
    luser_preference.add_flag(user_preference.FLAG_IS_NOT_ZEROABLE)
    luser_preference.save()
    user_preference_threshold.create(user, user_preference=luser_preference, num_days=1, min_value=15)
    return luser_preference


def get_nutrient_preference() -> user_preference.UserPreference:
    """Get nutrient preference (with threshold)."""
    user: user_model.User = get_user()
    luser_preference: user_preference.UserPreference = user_preference.create(
        user, food_nutrient_id=constants.ENERGY_NUTRIENT_ID
    )
    user_preference_threshold.create(user, user_preference=luser_preference, num_days=1, min_value=1000)
    return luser_preference


def get_category_preference() -> user_preference.UserPreference:
    """Get category preference (with threshold)."""
    user: user_model.User = get_user()
    luser_preference: user_preference.UserPreference = user_preference.create(user, food_category_id=1)
    user_preference_threshold.create(user, user_preference=luser_preference, num_days=1, min_value=50)
    return luser_preference


def get_user_recipe_preference() -> user_preference.UserPreference:
    """Get user recipe preference (with threshold)."""
    user: user_model.User = get_user()
    lrecipe: user_recipe.UserRecipe = get_recipe()
    luser_preference: user_preference.UserPreference = user_preference.create(
        user, food_external_id=lrecipe.external_id
    )
    luser_preference.add_flag(user_preference.FLAG_IS_AVAILABLE)
    luser_preference.save()
    user_preference_threshold.create(user, user_preference=luser_preference, num_days=1, min_value=5)
    return luser_preference


#
# Search results objects
#
def get_search_result_1() -> search_result.SearchResult:
    """Get Search Result."""
    return search_result.create(
        external_id=test_constants.TEST_UUID,
        name="search_result_1",
        brand_name="brand_name",
        brand_owner="brand_owner",
        gtin_upc="gtin_upc",
    )


def get_search_result_2() -> search_result.SearchResult:
    """Get Search Result 2."""
    return search_result.create(external_id=test_constants.TEST_UUID_2, name="search_result_2")


def index_cfood() -> None:
    """Create a branded db food and index it in search."""
    cfood = get_db_food()
    get_db_branded_food()
    search_indexing.convert_to_search_result(cfood).save()
    search_result.update_search_vector()


#
# API related objects
#
def get_api_key() -> str:
    """Get test API Key."""
    _, key = APIKey.objects.create_key(name="test")
    return key
