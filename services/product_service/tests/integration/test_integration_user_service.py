import uuid
import pytest

@pytest.mark.asyncio
async def test_create_product_with_valid_seller(user_client, product_client):
    email = f"seller_{uuid.uuid4().hex[:8]}@test.com"
    seller_resp = await user_client.post("/auth/sign_up", json={
        "first_name": "Test",
        "last_name": "Seller",
        "email": email,
        "password": "password",
        "role": "seller",
    })
    assert seller_resp.status_code == 201
    seller_id = seller_resp.json()["id"]

    category_resp = await product_client.post("/categories", json={
        "name": f"Cat-{uuid.uuid4().hex[:6]}",
        "description": "test",
    })
    assert category_resp.status_code == 201
    category_id = category_resp.json()["id"]

    product_resp = await product_client.post(
        f"/products/?seller_id={seller_id}&category_id={category_id}",
        json={"name": "Item", "price": 10, "stock": 5},
    )
    assert product_resp.status_code == 201
    assert product_resp.json()["name"] == "Item"


@pytest.mark.asyncio
async def test_create_product_rejects_non_seller(user_client, product_client):
    email = f"user_{uuid.uuid4().hex[:8]}@test.com"
    user_resp = await user_client.post("/auth/sign_up", json={
        "first_name": "Test", "last_name": "User",
        "email": email, "password": "password", "role": "user",
    })
    user_id = user_resp.json()["id"]

    # category_id — любой существующий
    product_resp = await product_client.post(
        f"/products/?seller_id={user_id}&category_id=CATEGORY_ID",
        json={"name": "Item", "price": 10, "stock": 5},
    )
    assert product_resp.status_code == 403