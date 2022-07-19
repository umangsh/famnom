"""URL configuration for nutrition_tracker API."""
from __future__ import annotations

from django.urls import include, path, re_path
from rest_framework import routers

from nutrition_tracker.rest_framework.views import (
    APIAppConstants,
    APIDeleteUserIngredient,
    APIDeleteUserMeal,
    APIDeleteUserRecipe,
    APIDetailsDBFood,
    APIDetailsUserIngredient,
    APIDetailsUserMeal,
    APIDetailsUserRecipe,
    APIEditUserIngredient,
    APIEditUserMeal,
    APIEditUserRecipe,
    APILogDBFood,
    APILogUserIngredient,
    APILogUserRecipe,
    APIMealplanFormOne,
    APIMealplanFormThree,
    APIMealplanFormTwo,
    APIMyFoods,
    APIMyMeals,
    APIMyNutrition,
    APIMyRecipes,
    APINutrient,
    APINutritionFDA,
    APINutritionLabel,
    APINutritionPreference,
    APISaveDBFood,
    APISearchResults,
    APITracker,
)

router = routers.SimpleRouter()

urlpatterns = [
    path("", include(router.urls)),
    path("config/appconstants/", APIAppConstants.as_view(), name="api_app_constants"),
    path("config/nutrition/fda/", APINutritionFDA.as_view(), name="api_nutrition_fda"),
    path("config/nutrition/label/", APINutritionLabel.as_view(), name="api_nutrition_label"),
    path("delete/useringredient/<uuid:id>/", APIDeleteUserIngredient.as_view(), name="api_delete_user_ingredient"),
    path(
        "delete/useringredient/<uuid:id>/<uuid:mid>/",
        APIDeleteUserIngredient.as_view(),
        name="api_delete_user_ingredient",
    ),
    path("delete/usermeal/<uuid:id>/", APIDeleteUserMeal.as_view(), name="api_delete_user_meal"),
    path("delete/userrecipe/<uuid:id>/", APIDeleteUserRecipe.as_view(), name="api_delete_user_recipe"),
    path("delete/userrecipe/<uuid:id>/<uuid:mid>/", APIDeleteUserRecipe.as_view(), name="api_delete_user_recipe"),
    path("details/dbfood/<uuid:id>/", APIDetailsDBFood.as_view(), name="api_details_db_food"),
    path("details/useringredient/<uuid:id>/", APIDetailsUserIngredient.as_view(), name="api_details_user_ingredient"),
    path(
        "details/useringredient/<uuid:id>/<uuid:mid>/",
        APIDetailsUserIngredient.as_view(),
        name="api_details_user_ingredient",
    ),
    path("details/usermeal/<uuid:id>/", APIDetailsUserMeal.as_view(), name="api_details_user_meal"),
    path("details/userrecipe/<uuid:id>/", APIDetailsUserRecipe.as_view(), name="api_details_user_recipe"),
    path("details/userrecipe/<uuid:id>/<uuid:mid>/", APIDetailsUserRecipe.as_view(), name="api_details_user_recipe"),
    path("edit/useringredient/", APIEditUserIngredient.as_view(), name="api_edit_user_ingredient"),
    path("edit/useringredient/<uuid:id>/", APIEditUserIngredient.as_view(), name="api_edit_user_ingredient"),
    path("edit/usermeal/", APIEditUserMeal.as_view(), name="api_edit_user_meal"),
    path("edit/usermeal/<uuid:id>/", APIEditUserMeal.as_view(), name="api_edit_user_meal"),
    path("edit/userrecipe/", APIEditUserRecipe.as_view(), name="api_edit_user_recipe"),
    path("edit/userrecipe/<uuid:id>/", APIEditUserRecipe.as_view(), name="api_edit_user_recipe"),
    path("log/dbfood/<uuid:id>/", APILogDBFood.as_view(), name="api_log_db_food"),
    path("log/useringredient/<uuid:id>/", APILogUserIngredient.as_view(), name="api_log_user_ingredient"),
    path("log/useringredient/<uuid:id>/<uuid:mid>/", APILogUserIngredient.as_view(), name="api_log_user_ingredient"),
    path("log/userrecipe/<uuid:id>/", APILogUserRecipe.as_view(), name="api_log_user_recipe"),
    path("log/userrecipe/<uuid:id>/<uuid:mid>/", APILogUserRecipe.as_view(), name="api_log_user_recipe"),
    path("myfoods/", APIMyFoods.as_view(), name="api_my_foods"),
    path("mymeals/", APIMyMeals.as_view(), name="api_my_meals"),
    path("mynutrition/", APIMyNutrition.as_view(), name="api_my_nutrition"),
    path("myrecipes/", APIMyRecipes.as_view(), name="api_my_recipes"),
    path("nutrient/<int:id>/", APINutrient.as_view(), name="api_nutrient"),
    path("nutrient/<int:id>/<int:days>/", APINutrient.as_view(), name="api_nutrient"),
    path("preferences/nutrition/", APINutritionPreference.as_view(), name="api_nutrition_preference"),
    path("savedbfood/", APISaveDBFood.as_view(), name="api_save_db_food"),
    path("savemealplan/formone/", APIMealplanFormOne.as_view(), name="api_mealplan_form_one"),
    path("savemealplan/formtwo/", APIMealplanFormTwo.as_view(), name="api_mealplan_form_two"),
    path("savemealplan/formthree/", APIMealplanFormThree.as_view(), name="api_mealplan_form_three"),
    path("search/", APISearchResults.as_view(), name="api_search"),
    re_path(r"^tracker/(?P<td>\d{4}-\d{2}-\d{2})/$", APITracker.as_view(), name="api_tracker"),
]
