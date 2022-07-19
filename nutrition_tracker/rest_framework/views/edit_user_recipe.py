"""Edit User Recipe REST API view."""
from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from nutrition_tracker.forms import FoodMemberFormset, FoodPortionFormset, RecipeMemberFormset
from nutrition_tracker.logic import data_loaders
from nutrition_tracker.models import user_recipe
from nutrition_tracker.serializers import RecipeFormSerializer, UserRecipeMutableSerializer


class APIEditUserRecipe(APIView):
    """Edit User Recipe REST API response."""

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """GET request handler."""
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        external_id = self.kwargs.get("id")
        if not external_id:
            # Create flow
            return Response(status=status.HTTP_200_OK)

        lrecipe = user_recipe.load_lrecipe(request.user, external_id=external_id)
        if not lrecipe:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        lfoods = list(data_loaders.load_lfoods_for_lparents(request.user, [lrecipe]))
        member_recipes = list(data_loaders.load_lrecipes_for_lparents(request.user, [lrecipe]))
        serializer = UserRecipeMutableSerializer(
            instance=lrecipe, context={"lparent": lrecipe, "lfoods": lfoods, "lrecipes": member_recipes}
        )
        return Response(serializer.data, status.HTTP_200_OK)

    def post(  # pylint: disable=too-many-return-statements
        self, request: Request, *args: Any, **kwargs: Any
    ) -> Response:
        """POST request handler."""
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        lrecipe = user_recipe.load_lrecipe(request.user, external_id=request.data.get("external_id"))
        serializer = RecipeFormSerializer(
            data=request.data,
            context={
                "user": request.user,
                "lrecipe": lrecipe,
            },
        )

        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        servings = FoodPortionFormset(request.data, instance=lrecipe, prefix="servings")
        if not servings.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        lfoods = []
        member_recipes = []
        if lrecipe:
            lfoods = list(data_loaders.load_lfoods_for_lparents(request.user, [lrecipe]))
            member_recipes = list(data_loaders.load_lrecipes_for_lparents(request.user, [lrecipe]))

        food_members = FoodMemberFormset(
            request.data, instance=lrecipe, prefix="food", form_kwargs={"lparent": lrecipe, "lfoods": lfoods}
        )
        if not food_members.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        recipe_members = RecipeMemberFormset(
            request.data,
            instance=lrecipe,
            prefix="recipe",
            form_kwargs={"lparent": lrecipe, "lrecipes": member_recipes},
        )
        if not recipe_members.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        lrecipe = serializer.form_instance.save(servings, food_members, recipe_members)
        if lrecipe:
            return Response(lrecipe.external_id, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)
