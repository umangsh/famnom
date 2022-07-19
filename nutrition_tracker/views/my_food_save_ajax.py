"""Save a DBFood as an ingredient in user's kitchen (Ajax view)."""
from __future__ import annotations

from http import HTTPStatus
from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

import users.models as user_model
from nutrition_tracker.constants import constants
from nutrition_tracker.forms import UUIDForm
from nutrition_tracker.models import db_food, user_ingredient
from nutrition_tracker.utils import views as views_util


class MyFoodSaveAjaxView(LoginRequiredMixin, TemplateView):
    """My foods save ajax view class."""

    form_class = UUIDForm

    def get(self, *args: Any, **kwargs: Any) -> HttpResponse:
        messages.add_message(self.request, messages.ERROR, constants.MESSAGE_ERROR_UNSUPPORTED_ACTION)
        return redirect(constants.URL_HOME)

    @method_decorator(views_util.ajax_login_required)
    def post(self, *args: Any, **kwargs: Any) -> HttpResponse | JsonResponse:
        """View post."""
        if not views_util.is_ajax(self.request):
            messages.add_message(self.request, messages.ERROR, constants.MESSAGE_ERROR_UNSUPPORTED_ACTION)
            return redirect(constants.URL_SEARCH)

        luser: user_model.User = self.request.user  # type: ignore
        form = self.form_class(self.request.POST)
        if form.is_valid():
            self.external_id = form.cleaned_data["id"]  # pylint: disable=attribute-defined-outside-init
        else:
            return JsonResponse({}, status=HTTPStatus.BAD_REQUEST)

        cfood: db_food.DBFood | None = db_food.load_cfood(external_id=self.external_id)
        if not cfood:
            return JsonResponse({})

        lfood: user_ingredient.UserIngredient | None = user_ingredient.load_lfood(luser, db_food_id=cfood.id)
        if not lfood:
            user_ingredient.create(luser=luser, db_food=cfood)

        return JsonResponse({})
