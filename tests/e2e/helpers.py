"""Shared helpers for e2e scenarios (auth, assertions, domain setup)."""

from __future__ import annotations

import uuid
import pytest
import httpx


def assert_status(response: httpx.Response, expected: int, message: str = "") -> None:
    assert response.status_code == expected, (
        f"Expected {expected}, got {response.status_code}. {message}. "
        f"Response: {response.text}"
    )

def assert_cart_structure(
    cart: dict,
    *,
    expected_items: list[str] = None,
    expected_total: float = None,
) -> None:
    assert len(cart["items"]) == (len(expected_items) if expected_items else 0), f"expected {len(expected_items)} items, got {len(cart['items'])}"
    for item in cart["items"]:
        assert item["product_id"] in expected_items, f"expected product {item['product_id']} in {expected_items}"
    assert cart["total"] == (expected_total if expected_total else 0.0), f"expected total {expected_total}, got {cart['total']}"


def assert_product_structure(
    product: dict,
    *,
    expected_name: str | None = None,
    expected_price: float | None = None,
    expected_stock: int | None = None,
    expected_description: str | None = None,
    expected_available: bool | None = None,
) -> None:
    if expected_name is not None:
        assert product["name"] == expected_name, (
            f"expected name {expected_name}, got {product['name']}"
        )
    if expected_price is not None:
        assert product["price"] == expected_price, (
            f"expected price {expected_price}, got {product['price']}"
        )
    if expected_stock is not None:
        assert product["stock"] == expected_stock, (
            f"expected stock {expected_stock}, got {product['stock']}"
        )
    if expected_description is not None:
        assert product.get("description") == expected_description, (
            f"expected description {expected_description}, got {product.get('description')}"
        )
    if expected_available is not None:
        assert product["available"] == expected_available, (
            f"expected available {expected_available}, got {product['available']}"
        )


def unique_email(prefix: str = "e2e") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}@example.com"


def unique_name(prefix: str = "E2E") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def cart_total(body: dict) -> float:
    """Cart schema uses `total` with alias `total_price`."""
    value = body.get("total", body.get("total_price"))
    assert value is not None, f"cart total missing in response: {body}"
    return float(value)


async def sign_up(
    user_client: httpx.AsyncClient,
    *,
    role: str = "user",
    email: str | None = None,
    password: str = "password",
    first_name: str = "E2E",
    last_name: str = "User",
) -> tuple[dict, str]:
    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email or unique_email(role),
        "password": password,
        "role": role,
    }
    response = await user_client.post("/auth/sign_up", json=payload)
    assert_status(response, 201, f"sign_up failed for {payload['email']}")
    return response.json(), password


async def sign_in_headers(
    user_client: httpx.AsyncClient,
    email: str,
    password: str,
) -> dict[str, str]:
    response = await user_client.post(
        "/auth/sign_in",
        data={"username": email, "password": password},
    )
    assert_status(response, 200, f"sign_in failed for {email}")
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def sign_up_and_auth(
    user_client: httpx.AsyncClient,
    *,
    role: str = "user",
    password: str = "password",
) -> tuple[dict, dict[str, str]]:
    """Register user and return (user_json, bearer_headers)."""
    user, plain = await sign_up(user_client, role=role, password=password)
    headers = await sign_in_headers(user_client, user["email"], plain)
    return user, headers


async def create_category(
    product_client: httpx.AsyncClient,
    name: str | None = None,
    description: str = "e2e",
) -> dict:
    response = await product_client.post(
        "/categories/",
        json={"name": name or unique_name("Cat"), "description": description},
    )
    assert_status(response, 201, "create category failed")
    return response.json()


async def create_product(
    product_client: httpx.AsyncClient,
    *,
    seller_id: str,
    category_id: str,
    name: str | None = None,
    price: float = 10.0,
    stock: int = 5,
    description: str | None = None,
) -> dict:
    payload: dict = {
        "name": name or unique_name("Item"),
        "price": price,
        "stock": stock,
    }
    if description is not None:
        payload["description"] = description
    response = await product_client.post(
        f"/products/?seller_id={seller_id}&category_id={category_id}",
        json=payload,
    )
    assert_status(response, 201, "create product failed")
    return response.json()


async def add_to_cart(
    cart_client: httpx.AsyncClient,
    *,
    user_id: str,
    product_id: str,
    quantity: int = 1,
    price: float = 10.0,
) -> dict:
    response = await cart_client.post(
        f"/cart/{user_id}/{product_id}",
        json={"quantity": quantity, "price": price},
    )
    assert_status(response, 201, "add to cart failed")
    return response.json()
