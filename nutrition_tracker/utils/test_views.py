from __future__ import annotations

from http import HTTPStatus
from unittest.mock import Mock

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.test.client import RequestFactory

from nutrition_tracker.tests import objects as test_objects
from nutrition_tracker.utils import views as views_util


class TestUtilsViews(TestCase):
    def test_is_ajax(self):
        request = RequestFactory().get("/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertTrue(views_util.is_ajax(request))

    def test_is_ajax_fails(self):
        request = RequestFactory().get("/")
        self.assertFalse(views_util.is_ajax(request))

    def test_ajax_login_required(self):
        func = Mock()
        decorated_func = views_util.ajax_login_required(func)

        luser = test_objects.get_user()
        request = RequestFactory().get("/")
        request.user = luser
        decorated_func(request)
        func.assert_called_once()

    def test_ajax_login_required_redirect(self):
        func = Mock()
        decorated_func = views_util.ajax_login_required(func)

        request = RequestFactory().get("/")
        request.user = AnonymousUser()
        response = decorated_func(request)
        func.assert_not_called()
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
        self.assertJSONEqual(response.content.decode("utf8"), {})
