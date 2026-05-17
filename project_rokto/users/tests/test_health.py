from __future__ import annotations

from http import HTTPStatus
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.db import connections
from django.db.utils import OperationalError
from django.urls import resolve

from config.urls import health


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_returns_ok(self, client, db):
        """Health endpoint returns 200 when database is reachable."""
        response = client.get("/health")
        assert response.status_code == HTTPStatus.OK
        assert response.content.decode() == "ok"

    def test_health_returns_503_on_db_failure(self, db):
        """Health endpoint returns 503 when database is unreachable."""
        # Patch ensure_connection only on the default connection object,
        # not on the class. The db fixture ensures DB is accessible so
        # Django's internal calls to get_autocommit() -> ensure_connection()
        # will work normally through the real connection.
        with patch.object(
            connections["default"],
            "ensure_connection",
            side_effect=OperationalError("Unable to connect"),
        ):
            response = health(_mock_request())
        assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE
        assert "Database connection failed" in response.content.decode()

    def test_health_resolves_correctly(self):
        """Health URL resolves to the correct view function."""
        match = resolve("/health")
        assert match.func.__name__ == "health"
        assert match.url_name is None  # health is a direct path, not a named URL


class TestWaitForDbCommand:
    """Tests for the wait_for_db management command."""

    def test_wait_for_db_succeeds_immediately(self, db):
        """Command succeeds immediately when database is available."""
        call_command("wait_for_db", timeout=5)

    def test_wait_for_db_timeout(self):
        """Command raises TimeoutError when database is not available."""
        with patch(
            "django.db.backends.base.base.BaseDatabaseWrapper.ensure_connection",
        ) as mock:
            mock.side_effect = OperationalError("Unable to connect")
            with pytest.raises(TimeoutError, match="Database not available after"):
                call_command("wait_for_db", timeout=1, interval=0.1)

    def test_wait_for_db_eventually_succeeds(self):
        """Command succeeds after database becomes available."""
        attempts = [True, True, False]  # First two fail, third succeeds

        def _connect():
            if attempts:
                if attempts.pop(0):
                    msg = "Unable to connect"
                    raise OperationalError(msg)

        with (
            patch(
                "django.db.backends.base.base.BaseDatabaseWrapper.ensure_connection",
            ) as mock,
            patch(
                "django.db.backends.base.base.BaseDatabaseWrapper.cursor",
            ) as mock_cursor,
        ):
            mock.side_effect = _connect
            mock_cursor.return_value.__enter__.return_value = mock_cursor.return_value
            call_command("wait_for_db", timeout=5, interval=0.1)


def _mock_request():
    """Create a minimal mock request for testing the health view directly."""
    request = MagicMock()
    request.META = {}
    request.method = "GET"
    return request
