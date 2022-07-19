"""Admin modules init."""
from .db_branded_food import DBBrandedFoodAdmin
from .db_food import DBFoodAdmin
from .db_food_nutrient import DBFoodNutrientAdmin
from .db_food_portion import DBFoodPortionAdmin
from .search_result import SearchResultAdmin
from .usda_branded_food import USDABrandedFoodAdmin
from .usda_fndds_food import USDAFnddsFoodAdmin
from .usda_food import USDAFoodAdmin
from .usda_food_nutrient import USDAFoodNutrientAdmin
from .usda_food_portion import USDAFoodPortionAdmin
from .usda_foundation_food import USDAFoundationFoodAdmin
from .usda_sr_legacy import USDASRLegacyAdmin
from .user_branded_food import UserBrandedFoodAdmin
from .user_food_portion import UserFoodPortionAdminInline
from .user_food_membership import UserFoodMembershipAdmin  # noqa I100. UserFoodPortionAdminInline is imported first.
from .user_food_membership import UserFoodMembershipChildAdminInline
from .user_food_membership import UserFoodMembershipParentAdminInline
from .user_food_nutrient import UserFoodNutrientAdmin
from .user_food_portion import UserFoodPortionAdmin
from .user_ingredient import UserIngredientAdmin
from .user_meal import UserMealAdmin
from .user_preference_threshold import UserPreferenceThresholdAdminInline
from .user_preference import UserPreferenceAdmin  # noqa I100. UserPreferenceThresholdAdminInline is imported first
from .user_preference_threshold import UserPreferenceThreshold
from .user_recipe import UserRecipeAdmin
