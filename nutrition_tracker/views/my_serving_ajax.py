"""Ajax view to lookup food portions for foods/recipes."""
from __future__ import annotations

from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

import users.models as user_model
from nutrition_tracker.constants import constants
from nutrition_tracker.logic import forms as forms_logic
from nutrition_tracker.models import db_food, user_ingredient, user_recipe
from nutrition_tracker.utils import views as views_util


class MyServingAjaxView(LoginRequiredMixin, TemplateView):
    """My serving ajax view class."""

    @method_decorator(views_util.ajax_login_required)
    def get(self, *args: Any, **kwargs: Any) -> HttpResponse:
        if not views_util.is_ajax(self.request):
            messages.add_message(self.request, messages.ERROR, constants.MESSAGE_ERROR_UNSUPPORTED_ACTION)
            return redirect(constants.URL_HOME)

        luser: user_model.User = self.request.user  # type: ignore
        external_id: str | None = kwargs.get("id")
        lobject: user_ingredient.UserIngredient | user_recipe.UserRecipe | None = user_ingredient.load_lfood(
            luser, external_id=external_id
        )
        if not lobject:
            lobject = user_recipe.load_lrecipe(luser, external_id=external_id)

        if not lobject:
            return JsonResponse({})

        cfood: db_food.DBFood | None = getattr(lobject, "db_food", None)
        portion_choices = forms_logic.get_portion_choices_form_data(lobject, cfood=cfood)
        return JsonResponse(portion_choices, safe=False)
