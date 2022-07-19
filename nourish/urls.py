"""URL configuration for nutrition_tracker."""
from __future__ import annotations

from decouple import config
from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.templatetags.static import static
from django.urls import include, path
from django.views.generic import RedirectView, TemplateView

from nutrition_tracker import sitemaps
from nutrition_tracker.constants import constants
from nutrition_tracker.views import (
    errors,
    index,
    my_available_foods_ajax,
    my_barcode_ajax,
    my_food,
    my_food_create,
    my_food_delete,
    my_food_edit,
    my_food_log,
    my_food_save_ajax,
    my_foods,
    my_ingredient,
    my_ingredient_log,
    my_meal,
    my_meal_create,
    my_meal_delete,
    my_meal_edit,
    my_mealplan,
    my_meals,
    my_nutrient_ajax,
    my_nutrition,
    my_profile,
    my_recent_foods_ajax,
    my_recipe,
    my_recipe_create,
    my_recipe_delete,
    my_recipe_edit,
    my_recipe_log,
    my_recipes,
    my_serving_ajax,
    my_suggested_foods_ajax,
    my_tracker_ajax,
    nutrient,
    robots_txt,
    search,
    top_foods_ajax,
)

sitemaps_map = {
    "static": sitemaps.StaticSitemap(),
}

urlpatterns = [
    # Include dj_rest_auth URLs before allauth urls, to avoid mangling confirm email URL.
    path("api/", include("nutrition_tracker.urls")),
    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/auth/registration/", include("dj_rest_auth.registration.urls")),
    path("accounts/", include("allauth.urls")),
    path("apple-touch-icon.png", RedirectView.as_view(url=static("nutrition_tracker/img/apple-touch-icon.png"))),
    path(
        "apple-touch-icon-precomposed.png",
        RedirectView.as_view(url=static("nutrition_tracker/img/apple-touch-icon-precomposed.png")),
    ),
    path("cookie_policy/", TemplateView.as_view(template_name="docs/cookie_policy.html"), name="cookie_policy"),
    path("favicon.ico", RedirectView.as_view(url=static("nutrition_tracker/img/favicon.ico"))),
    path(config("ADMIN_PATH"), admin.site.urls),
    path(
        "my_available_foods_ajax/<int:id>/",
        my_available_foods_ajax.MyAvailableFoodsAjaxView.as_view(),
        name="my_available_foods_ajax",
    ),
    path("my_barcode_ajax/<str:c>/", my_barcode_ajax.MyBarcodeAjaxView.as_view(), name="my_barcode_ajax"),
    path("my_food/<uuid:id>/", my_food.MyFoodView.as_view(), name=constants.URL_DETAIL_FOOD),
    path("my_food_create/", my_food_create.MyFoodCreateView.as_view(), name=constants.URL_CREATE_FOOD),
    path("my_food_delete/", my_food_delete.MyFoodDeleteView.as_view(), name=constants.URL_DELETE_FOOD),
    path("my_food_edit/<uuid:id>/", my_food_edit.MyFoodEditView.as_view(), name=constants.URL_EDIT_FOOD),
    path("my_food_log/<uuid:id>/", my_food_log.MyFoodLogView.as_view(), name=constants.URL_LOG_FOOD),
    path("my_food_save_ajax/", my_food_save_ajax.MyFoodSaveAjaxView.as_view(), name="my_food_save_ajax"),
    path("my_foods/", my_foods.MyFoodsView.as_view(), name=constants.URL_MY_FOODS),
    path("my_ingredient/<uuid:id>/", my_ingredient.MyIngredientView.as_view(), name=constants.URL_DETAIL_INGREDIENT),
    path(
        "my_ingredient/<uuid:id>/<uuid:mid>/",
        my_ingredient.MyIngredientView.as_view(),
        name=constants.URL_DETAIL_INGREDIENT,
    ),
    path(
        "my_ingredient_log/<uuid:id>/",
        my_ingredient_log.MyIngredientLogView.as_view(),
        name=constants.URL_LOG_INGREDIENT,
    ),
    path(
        "my_ingredient_log/<uuid:id>/<uuid:mid>/",
        my_ingredient_log.MyIngredientLogView.as_view(),
        name=constants.URL_LOG_INGREDIENT,
    ),
    path("my_meal/<uuid:id>/", my_meal.MyMealView.as_view(), name=constants.URL_DETAIL_MEAL),
    path("my_meal_create/", my_meal_create.MyMealCreateView.as_view(), name=constants.URL_CREATE_MEAL),
    path("my_meal_delete/", my_meal_delete.MyMealDeleteView.as_view(), name=constants.URL_DELETE_MEAL),
    path("my_meal_edit/<uuid:id>/", my_meal_edit.MyMealEditView.as_view(), name=constants.URL_EDIT_MEAL),
    path("my_mealplan/", my_mealplan.MyMealplanView.as_view(), name=constants.URL_MY_MEALPLAN),
    path("my_mealplan/<int:step>/", my_mealplan.MyMealplanView.as_view(), name=constants.URL_MY_MEALPLAN),
    path("my_meals/", my_meals.MyMealsView.as_view(), name=constants.URL_MY_MEALS),
    path("my_nutrient_ajax/<uuid:id>/", my_nutrient_ajax.MyNutrientAjaxView.as_view(), name="my_nutrient_ajax"),
    path("my_nutrition/", my_nutrition.MyNutritionView.as_view(), name=constants.URL_NUTRITION),
    path("my_profile/", my_profile.MyProfileView.as_view(), name=constants.URL_PROFILE),
    path(
        "my_recent_foods_ajax/<int:id>/",
        my_recent_foods_ajax.MyRecentFoodsAjaxView.as_view(),
        name="my_recent_foods_ajax",
    ),
    path("my_recipe/<uuid:id>/", my_recipe.MyRecipeView.as_view(), name=constants.URL_DETAIL_RECIPE),
    path("my_recipe/<uuid:id>/<uuid:mid>/", my_recipe.MyRecipeView.as_view(), name=constants.URL_DETAIL_RECIPE),
    path("my_recipe_create/", my_recipe_create.MyRecipeCreateView.as_view(), name=constants.URL_CREATE_RECIPE),
    path("my_recipe_delete/", my_recipe_delete.MyRecipeDeleteView.as_view(), name=constants.URL_DELETE_RECIPE),
    path("my_recipe_edit/<uuid:id>/", my_recipe_edit.MyRecipeEditView.as_view(), name=constants.URL_EDIT_RECIPE),
    path("my_recipe_log/<uuid:id>/", my_recipe_log.MyRecipeLogView.as_view(), name=constants.URL_LOG_RECIPE),
    path(
        "my_recipe_log/<uuid:id>/<uuid:mid>/", my_recipe_log.MyRecipeLogView.as_view(), name=constants.URL_LOG_RECIPE
    ),
    path("my_recipes/", my_recipes.MyRecipesView.as_view(), name=constants.URL_MY_RECIPES),
    path("my_serving_ajax/<uuid:id>/", my_serving_ajax.MyServingAjaxView.as_view(), name="my_serving_ajax"),
    path(
        "my_suggested_foods_ajax/",
        my_suggested_foods_ajax.MySuggestedFoodsAjaxView.as_view(),
        name="my_suggested_foods_ajax",
    ),
    path("my_tracker_ajax/<int:id>/", my_tracker_ajax.MyTrackerAjaxView.as_view(), name="my_tracker_ajax"),
    path("nutrient/<int:id>/", nutrient.NutrientView.as_view(), name=constants.URL_NUTRIENT),
    path("privacy_policy/", TemplateView.as_view(template_name="docs/privacy_policy.html"), name="privacy_policy"),
    path("robots.txt", robots_txt.robots_txt),
    path("search/", search.SearchResultsView.as_view(), name=constants.URL_SEARCH),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps_map}, name="django.contrib.sitemaps.views.sitemap"),
    path("terms_of_use/", TemplateView.as_view(template_name="docs/terms_of_use.html"), name="terms_of_use"),
    path("top_foods_ajax/<int:id>/", top_foods_ajax.TopFoodsAjaxView.as_view(), name="top_foods_ajax"),
    path("", index.HomepageView.as_view(), name=constants.URL_HOME),
]

handler404 = errors.NotFoundErrorView.as_view()
handler500 = errors.handler500

if settings.DJANGO_ENV == "dev":
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
