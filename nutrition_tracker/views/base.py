"""Base views module."""
from __future__ import annotations

from http import HTTPStatus
from typing import Any
from uuid import UUID

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Page
from django.db import transaction
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from nutrition_tracker.constants import constants
from nutrition_tracker.forms import LogForm, SearchForm, UUIDForm
from nutrition_tracker.models import user_meal, user_preference
from nutrition_tracker.utils import views as views_util


class FormBaseView(FormView):
    """Base form view."""

    def get_success_url(self, **kwargs: Any) -> str:
        messages.add_message(self.request, messages.SUCCESS, self.MESSAGE_SUCCESS)  # type: ignore
        return reverse_lazy(self.URL_SUCCESS, kwargs={"id": self.lobject.external_id})  # type: ignore

    def get_form_kwargs(self) -> dict:
        kwargs: dict = super().get_form_kwargs()
        kwargs.update(
            {
                "user": self.request.user,
            }
        )
        return kwargs


class CreateFormBaseView(FormBaseView):
    """Create form base view."""

    def get(self, *args: Any, **kwargs: Any) -> HttpResponse:
        self.load_data()  # type: ignore
        return super().get(*args, **kwargs)


class DeleteFormBaseView(FormView):
    """Delete form base view."""

    MESSAGE_NOT_ALLOWED: str = constants.MESSAGE_ERROR_DELETE_NOT_ALLOWED

    def get_success_url(self) -> str:
        messages.add_message(self.request, messages.SUCCESS, self.MESSAGE_SUCCESS)  # type: ignore
        if self.nexturl:
            return reverse_lazy(self.nexturl)

        return reverse_lazy(self.URL_SUCCESS)  # type: ignore

    def get(self, *args: Any, **kwargs: Any) -> HttpResponse:
        messages.add_message(self.request, messages.ERROR, self.MESSAGE_UNSUPPORTED_ACTION)  # type: ignore
        return redirect(self.URL_ERROR)  # type: ignore

    def form_invalid(self, form: UUIDForm) -> HttpResponse:
        messages.add_message(self.request, messages.ERROR, self.MESSAGE_INVALID_ID)  # type: ignore
        return redirect(self.URL_INVALID_ID)  # type: ignore

    def form_valid(self, form: UUIDForm) -> HttpResponse:
        external_id: UUID = form.cleaned_data["id"]
        mid: UUID | None = form.cleaned_data["mid"]
        nexturl: str | None = form.cleaned_data["nexturl"]

        self.nexturl = nexturl  # pylint: disable=attribute-defined-outside-init
        kwargs: dict[str, UUID | None] = {"id": external_id, "mid": mid}
        self.load_object(**kwargs)  # type: ignore
        if not self.lobject:  # type: ignore
            messages.add_message(self.request, messages.ERROR, self.MESSAGE_OBJECT_NOT_FOUND)  # type: ignore
            return redirect(self.URL_OBJECT_NOT_FOUND)  # type: ignore

        if self.request.user != self.lobject.user:  # type: ignore
            messages.add_message(self.request, messages.ERROR, self.MESSAGE_NOT_ALLOWED)
            return redirect(self.URL_NOT_ALLOWED)  # type: ignore

        if mid:
            if not self.lmembership:  # type: ignore
                messages.add_message(self.request, messages.ERROR, self.MESSAGE_NOT_ALLOWED)
                return redirect(self.URL_NOT_ALLOWED)  # type: ignore

            if self.request.user != self.lmembership.user:  # type: ignore
                messages.add_message(self.request, messages.ERROR, self.MESSAGE_NOT_ALLOWED)
                return redirect(self.URL_NOT_ALLOWED)  # type: ignore

            old_meal_id: int = self.lmembership.parent_id  # type: ignore
            self.lmembership.delete()  # type: ignore
            old_lmeal = user_meal.load_lmeal(self.request.user, id_=old_meal_id)  # type: ignore
            if old_lmeal and len(old_lmeal.members) == 0:  # type: ignore
                old_lmeal.delete()
        else:
            self.lobject.delete()  # type: ignore

        return super().form_valid(form)


class EditFormBaseView(FormBaseView):
    """Edit form base view."""

    @method_decorator(login_required)
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.POST:
            form: UUIDForm = UUIDForm({"id": request.POST.get("external_id")})
            if not form.is_valid():
                messages.add_message(request, messages.ERROR, self.MESSAGE_INVALID_ID)  # type: ignore
                return redirect(self.URL_INVALID_ID)  # type: ignore

            kwargs["id"] = self.external_id = form.cleaned_data["id"]  # pylint: disable=attribute-defined-outside-init

        self.load_object(**kwargs)  # type: ignore
        if not self.lobject:  # type: ignore
            messages.add_message(request, messages.ERROR, self.MESSAGE_OBJECT_NOT_FOUND)  # type: ignore
            return redirect(self.URL_OBJECT_NOT_FOUND)  # type: ignore

        self.load_data()  # type: ignore
        return super().dispatch(request, *args, **kwargs)


class LogFormBaseView(EditFormBaseView):
    """Log form base view."""

    def get_success_url(self, **kwargs: Any) -> str:
        messages.add_message(self.request, messages.SUCCESS, self.MESSAGE_LOG_SUCCESS)  # type: ignore
        return reverse_lazy(self.URL_LOG_SUCCESS)  # type: ignore

    @method_decorator(login_required)
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        self.lmeal = user_meal.load_latest_lmeal(  # pylint: disable=attribute-defined-outside-init
            request.user, timezone.localdate()
        )
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self) -> dict:
        kwargs: dict = super().get_form_kwargs()
        kwargs.update(
            {
                "external_id": self.external_id,
                "lobject": getattr(self, "lfood", None) or getattr(self, "lrecipe", None),
                "cfood": getattr(self, "cfood", None),
                "lmeal": self.lmeal,
                "lmembership": getattr(self, "lmembership", None),
                "food_portions": self.food_portions,  # type: ignore
            }
        )
        return kwargs

    def form_valid(self, form: LogForm) -> HttpResponse:
        with transaction.atomic():
            form.save()

        return super().form_valid(form)


class ListBaseView(ListView):
    """List base form view."""

    paginate_by: int = constants.PAGE_SIZE
    paginate_orphans: int = constants.PAGE_ORPHAN_SIZE

    def get(self, *args: Any, **kwargs: Any) -> HttpResponse | JsonResponse:
        form: SearchForm = SearchForm(self.request.GET)
        if not form.is_valid():
            if views_util.is_ajax(self.request):
                return JsonResponse({}, status=HTTPStatus.BAD_REQUEST)

            messages.add_message(self.request, messages.ERROR, constants.MESSAGE_ERROR_INVALID_SEARCH)
            return redirect(self.URL_INVALID_SEARCH)  # type: ignore

        self.query: str | None = form.cleaned_data["q"]  # pylint: disable=attribute-defined-outside-init
        flag_name: str | None = form.cleaned_data["fs"]
        self.flag_set = (  # pylint: disable=attribute-defined-outside-init
            flag_name if flag_name in user_preference.get_flag_names() else None
        )
        flag_name = form.cleaned_data["fn"]
        self.flag_unset = (  # pylint: disable=attribute-defined-outside-init
            flag_name if flag_name in user_preference.get_flag_names() else None
        )
        return super().get(*args, **kwargs)

    def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> HttpResponse | JsonResponse:
        if self.request.GET.get("format") == "json" or views_util.is_ajax(self.request):
            page_obj: Page = context["page_obj"]
            results: list = self.get_results(context)  # type: ignore
            data: dict[str, Any] = {"results": results, "pagination": {"more": page_obj.has_next()}}
            return JsonResponse(data)

        return super().render_to_response(context, **response_kwargs)


class TemplateBaseView(TemplateView):
    """Template base view."""

    def get(self, *args: Any, **kwargs: Any) -> HttpResponse:
        self.load_object(**kwargs)  # type: ignore
        if not self.lobject:  # type: ignore
            messages.add_message(self.request, messages.ERROR, self.MESSAGE_OBJECT_NOT_FOUND)  # type: ignore
            return redirect(self.URL_OBJECT_NOT_FOUND)  # type: ignore

        self.load_data()  # type: ignore
        return super().get(*args, **kwargs)


class NeverCacheMixin:  # pylint: disable=too-few-public-methods
    """Never cache view mixin."""

    @method_decorator(never_cache)
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Override dispatch."""
        return super().dispatch(request, *args, **kwargs)  # type: ignore
