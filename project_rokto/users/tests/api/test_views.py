from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from rest_framework.test import APIRequestFactory

from project_rokto.users.api.views import UserViewSet

if TYPE_CHECKING:
    from project_rokto.users.models import User


class TestUserViewSet:
    @pytest.fixture
    def api_rf(self) -> APIRequestFactory:
        return APIRequestFactory()

    def test_get_queryset(self, user: User, api_rf: APIRequestFactory):
        view = UserViewSet()
        request = api_rf.get("/fake-url/")
        request.user = user

        view.request = request

        assert user in view.get_queryset()

    def test_me(self, user: User, api_rf: APIRequestFactory):
        view = UserViewSet()
        request = api_rf.get("/fake-url/")
        request.user = user

        view.request = request

        response = view.me(request)  # type: ignore[call-arg, arg-type, misc]

        assert response.data == {
            "username": user.username,
            "url": f"http://testserver/api/users/{user.username}/",
            "name": user.name,
            "phone_number": user.phone_number,
            "blood_group": user.blood_group,
            "is_available_to_donate": user.is_available_to_donate,
            "preferred_locations": [],
        }
