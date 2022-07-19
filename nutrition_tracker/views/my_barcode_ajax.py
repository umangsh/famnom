"""Ajax view to lookup food barcodes."""
from __future__ import annotations

from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

import users.models as user_model
from nutrition_tracker.constants import constants
from nutrition_tracker.logic import search
from nutrition_tracker.models import search_result, user_branded_food
from nutrition_tracker.utils import url_factory
from nutrition_tracker.utils import views as views_util


class MyBarcodeAjaxView(LoginRequiredMixin, TemplateView):
    """My barcode ajax view class."""

    @method_decorator(views_util.ajax_login_required)
    def get(self, *args: Any, **kwargs: Any) -> HttpResponse:
        if not views_util.is_ajax(self.request):
            messages.add_message(self.request, messages.ERROR, constants.MESSAGE_ERROR_UNSUPPORTED_ACTION)
            return redirect(constants.URL_HOME)

        luser: user_model.User = self.request.user  # type: ignore
        barcode: str | None = kwargs.get("c")
        if not barcode:
            return JsonResponse({})

        lbranded_food: user_branded_food.UserBrandedFood | None = user_branded_food.load_lbranded_food(
            luser, gtin_upc=barcode
        )
        if lbranded_food:
            food_url: str = url_factory.get_ingredient_url(lbranded_food.ingredient.external_id)
            return JsonResponse({"url": food_url})

        s_results: QuerySet[search_result.SearchResult] = search.search_barcode(barcode)
        if s_results:
            s_result: search_result.SearchResult | None = s_results.first()
            if not s_result:
                return JsonResponse({})

            food_url = url_factory.get_food_url(s_result.external_id)
            return JsonResponse({"url": food_url})

        return JsonResponse({})
