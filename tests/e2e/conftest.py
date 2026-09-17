"""Pytest fixtures for marketplace e2e (black-box HTTP against Compose stack)."""

from __future__ import annotations
import asyncio

import pytest
import httpx

from tests.e2e.config import (
    CART_SERVICE_URL,
    HEALTH_POLL_INTERVAL_SEC,
    HEALTH_TIMEOUT_SEC,
    HTTP_CLIENT_TIMEOUT,
    PRODUCT_SERVICE_URL,
    USER_SERVICE_URL,
)


@pytest.fixture(scope="session")
async def user_client():
    async with httpx.AsyncClient(
        base_url=USER_SERVICE_URL,
        timeout=HTTP_CLIENT_TIMEOUT,
        follow_redirects=True,
    ) as client:
        yield client


@pytest.fixture(scope="session")
async def product_client():
    async with httpx.AsyncClient(
        base_url=PRODUCT_SERVICE_URL,
        timeout=HTTP_CLIENT_TIMEOUT,
        follow_redirects=True,
    ) as client:
        yield client


@pytest.fixture(scope="session")
async def cart_client():
    async with httpx.AsyncClient(
        base_url=CART_SERVICE_URL,
        timeout=HTTP_CLIENT_TIMEOUT,
        follow_redirects=True,
    ) as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
async def ensure_stack_ready(user_client, product_client, cart_client):
    """Ждём /healthcheck до первого теста."""
    for client in (user_client, product_client, cart_client):
        loop = asyncio.get_running_loop()
        deadline = loop.time() + HEALTH_TIMEOUT_SEC
        last_error: Exception | None = None

        while loop.time() < deadline:
            try:
                response = await client.get("/healthcheck")
                if response.status_code == 200:
                    return
                last_error = AssertionError(
                    f"Service {str(client.base_url)} /healthcheck returned {response.status_code}: {response.text}"
                )
            except (httpx.HTTPError, OSError) as exc:
                last_error = exc
            await asyncio.sleep(HEALTH_POLL_INTERVAL_SEC)

        raise TimeoutError(
            f"Service {str(client.base_url)} did not become healthy within {HEALTH_TIMEOUT_SEC}s. Last error: {last_error}"
        )


def pytest_collection_modifyitems(session, config, items):
    """Порядок выполнения тестов: smoke_health -> e2e (затем остальные)."""

    def weight(item):
        if "smoke_health" in item.nodeid:
            return 0
        return 1

    items.sort(key=weight)
