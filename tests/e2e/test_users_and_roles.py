"""E2E: auth, user CRUD and role-based access."""

from __future__ import annotations

import pytest

from tests.e2e.helpers import (
    assert_status,
    sign_in_headers,
    sign_up,
    sign_up_and_auth,
    unique_email,
)


class TestUsersAuth:
    """
    Tests for user authentication and authorization (/auth/sign_up and /auth/sign_in):
    - sign up and sign in returns tokens
    - sign up duplicate email conflict
    - sign in wrong password
    - my account requires JWT
    - user can update own name but not another user
    - admin can list users regular user cannot
    - admin can read and update any user
    - user can delete self admin can delete other
    - seller and admin roles are accepted on sign up
    """

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_sign_up_and_sign_in_returns_tokens(self, user_client):
        user, password = await sign_up(user_client, role="user")
        assert user["role"] == "user"
        assert user["active"] is True

        response = await user_client.post(
            "/auth/sign_in",
            data={"username": user["email"], "password": password},
        )
        assert_status(response, 200)
        tokens = response.json()
        assert tokens["access_token"]
        assert tokens.get("token_type", "Bearer").lower() == "bearer"


    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_sign_up_duplicate_email_conflict(self, user_client):
        email = unique_email("dup")
        await sign_up(user_client, email=email)
        again = await user_client.post(
            "/auth/sign_up",
            json={
                "first_name": "Dup",
                "last_name": "User",
                "email": email,
                "password": "password",
                "role": "user",
            },
        )
        assert_status(again, 409, "duplicate email must be 409")


    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_sign_in_wrong_password(self, user_client):
        user, _ = await sign_up(user_client)
        response = await user_client.post(
            "/auth/sign_in",
            data={"username": user["email"], "password": "wrong-password"},
        )
        assert_status(response, 401, "wrong password must be 401")


    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_my_account_requires_jwt(self, user_client):
        anonymous = await user_client.get("/users/account/my_account/")
        assert anonymous.status_code in {401, 403}

        user, headers = await sign_up_and_auth(user_client, role="user")
        me = await user_client.get("/users/account/my_account/", headers=headers)
        assert_status(me, 200)
        assert me.json()["id"] == user["id"]
        assert me.json()["email"] == user["email"]


    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_user_can_update_own_name_but_not_another_user(self, user_client):
        alice, alice_headers = await sign_up_and_auth(user_client, role="user")
        bob, _ = await sign_up(user_client, role="user")

        updated = await user_client.put(
            f"/users/{alice['id']}/name",
            headers=alice_headers,
            json={"first_name": "Alice", "last_name": "Updated"},
        )
        assert_status(updated, 200)
        assert updated.json()["first_name"] == "Alice"
        assert updated.json()["last_name"] == "Updated"

        forbidden = await user_client.put(
            f"/users/{bob['id']}/name",
            headers=alice_headers,
            json={"first_name": "Hacker"},
        )
        assert_status(forbidden, 403, "user must not update another user")


    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_admin_can_list_users_regular_user_cannot(self, user_client):
        admin, admin_headers = await sign_up_and_auth(user_client, role="admin")
        regular, regular_headers = await sign_up_and_auth(user_client, role="user")

        forbidden = await user_client.get("/users/", headers=regular_headers)
        assert_status(forbidden, 403, "non-admin must not list users")

        listed = await user_client.get(
            "/users/",
            headers=admin_headers,
            params={"user_role": "user", "limit": 100},
        )
        assert_status(listed, 200)
        ids = {u["id"] for u in listed.json()}
        assert regular["id"] in ids
        assert admin["id"] not in ids  # filtered by user_role=user


    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_admin_can_read_and_update_any_user(self, user_client):
        admin, admin_headers = await sign_up_and_auth(user_client, role="admin")
        target, _ = await sign_up(user_client, role="user", first_name="Target")

        got = await user_client.get(f"/users/{target['id']}", headers=admin_headers)
        assert_status(got, 200)
        assert got.json()["id"] == target["id"]

        new_email = unique_email("admin-rename")
        renamed = await user_client.put(
            f"/users/{target['id']}/email",
            headers=admin_headers,
            json={"id": target["id"], "email": new_email},
        )
        assert_status(renamed, 200)
        assert renamed.json()["email"] == new_email


    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_user_can_delete_self_admin_can_delete_other(self, user_client):
        victim, victim_headers = await sign_up_and_auth(user_client, role="user")
        deleted = await user_client.delete(
            f"/users/{victim['id']}",
            headers=victim_headers,
        )
        assert_status(deleted, 200)

        admin, admin_headers = await sign_up_and_auth(user_client, role="admin")
        other, _ = await sign_up(user_client, role="user")
        admin_delete = await user_client.delete(
            f"/users/{other['id']}",
            headers=admin_headers,
        )
        assert_status(admin_delete, 200)

        missing = await user_client.get(f"/users/{other['id']}", headers=admin_headers)
        assert_status(missing, 404)


    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_seller_and_admin_roles_are_accepted_on_sign_up(self, user_client):
        seller, _ = await sign_up(user_client, role="seller")
        admin, _ = await sign_up(user_client, role="admin")
        assert seller["role"] == "seller"
        assert admin["role"] == "admin"

        seller_headers = await sign_in_headers(user_client, seller["email"], "password")
        response = await user_client.get("/users/account/my_account/", headers=seller_headers)
        assert_status(response, 200)
        assert response.json()["role"] == "seller"

        admin_headers = await sign_in_headers(user_client, admin["email"], "password")
        response = await user_client.get("/users/account/my_account/", headers=admin_headers)
        assert_status(response, 200)
        assert response.json()["role"] == "admin"
