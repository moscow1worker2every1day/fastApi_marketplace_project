"""Tests for service startup readiness."""

import pytest
import httpx
from tests.helpers import APP_VERSION, OPENAPI_PATHS, _assert_status_200, _assert_status_422


class TestStartupService:
    """Tests that the service started and is ready to accept requests."""

    @pytest.mark.asyncio
    async def test_healthcheck_returns_ok(self, client: httpx.AsyncClient):
        """Healthcheck must be available after successful startup."""
        response = await client.get("/healthcheck")

        _assert_status_200(response)
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data
        assert isinstance(data["version"], str)
        assert data["version"]

    @pytest.mark.asyncio
    async def test_healthcheck_version_matches_deploy(self, client: httpx.AsyncClient):
        """Version from healthcheck should match DEPLOY_VERSION."""
        response = await client.get("/healthcheck")

        _assert_status_200(response)
        assert response.json()["version"] == APP_VERSION

    @pytest.mark.asyncio
    async def test_openapi_schema_available(self, client: httpx.AsyncClient):
        """OpenAPI schema must be published after app startup."""
        response = await client.get("/openapi.json")

        _assert_status_200(response)
        schema = response.json()
        assert schema["info"]["title"] == "User Service"
        assert schema["info"]["version"] == APP_VERSION
        assert "paths" in schema

    @pytest.mark.asyncio
    async def test_openapi_contains_expected_routes(self, client: httpx.AsyncClient):
        """All critical auth/users/technical routes must be registered."""
        response = await client.get("/openapi.json")

        _assert_status_200(response)
        paths = set(response.json()["paths"].keys())
        missing = OPENAPI_PATHS - paths
        assert not missing, f"Missing OpenAPI paths after startup: {missing}"

    @pytest.mark.asyncio
    async def test_swagger_docs_available(self, client: httpx.AsyncClient):
        """Swagger UI must be available after startup."""
        response = await client.get("/docs")
        _assert_status_200(response)
        assert "text/html" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_redoc_available(self, client: httpx.AsyncClient):
        """ReDoc must be available after startup."""
        response = await client.get("/redoc")
        _assert_status_200(response)
        assert "text/html" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_service_accepts_api_requests(self, client: httpx.AsyncClient):
        """
        After DB connection + migrations, API must respond without 5xx.
        Invalid payload -> 422 means app and validation pipeline are up.
        """
        response = await client.post("/auth/sign_up", json={})
        _assert_status_422(response)
        assert response.status_code < 500
