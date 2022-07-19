"""Edit User Meal REST API view."""
from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from nutrition_tracker.forms import FoodMemberFormset, RecipeMemberFormset
from nutrition_tracker.logic import data_loaders
from nutrition_tracker.models import user_meal
from nutrition_tracker.serializers import MealFormSerializer, UserMealMutableSerializer


class APIEditUserMeal(APIView):
    """Edit User Meal REST API response."""

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """GET request handler."""
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        external_id = self.kwargs.get("id")
        if not external_id:
            # Create flow
            return Response(status=status.HTTP_200_OK)

        lmeal = user_meal.load_lmeal(request.user, external_id=external_id)
        if not lmeal:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        lfoods = list(data_loaders.load_lfoods_for_lparents(request.user, [lmeal]))
        member_recipes = list(data_loaders.load_lrecipes_for_lparents(request.user, [lmeal]))
        serializer = UserMealMutableSerializer(
            instance=lmeal, context={"lparent": lmeal, "lfoods": lfoods, "lrecipes": member_recipes}
        )
        return Response(serializer.data, status.HTTP_200_OK)

    def post(  # pylint: disable=too-many-return-statements
        self, request: Request, *args: Any, **kwargs: Any
    ) -> Response:
        """POST request handler."""
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        lmeal = user_meal.load_lmeal(request.user, external_id=request.data.get("external_id"))
        serializer = MealFormSerializer(
            data=request.data,
            context={
                "user": request.user,
                "lmeal": lmeal,
            },
        )

        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        lfoods = []
        member_recipes = []
        if lmeal:
            lfoods = list(data_loaders.load_lfoods_for_lparents(request.user, [lmeal]))
            member_recipes = list(data_loaders.load_lrecipes_for_lparents(request.user, [lmeal]))

        food_members = FoodMemberFormset(
            request.data, instance=lmeal, prefix="food", form_kwargs={"lparent": lmeal, "lfoods": lfoods}
        )
        if not food_members.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        recipe_members = RecipeMemberFormset(
            request.data,
            instance=lmeal,
            prefix="recipe",
            form_kwargs={"lparent": lmeal, "lrecipes": member_recipes},
        )
        if not recipe_members.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        lmeal = serializer.form_instance.save(food_members, recipe_members)
        if lmeal:
            return Response(lmeal.external_id, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)
