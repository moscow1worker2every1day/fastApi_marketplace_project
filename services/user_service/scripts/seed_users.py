"""
Bulk-seed users into Postgres.

Inside Docker (preferred — uses container env / postgres_user host):

    docker compose exec user_service python -m scripts.seed_users
    docker compose exec user_service python -m scripts.seed_users --count 100000
    docker compose exec user_service python -m scripts.seed_users --clear

From host (uses services/user_service/.env):

    python -m scripts.seed_users

Creates:
  - load_admin@example.com (role=admin)
  - load_user_0@example.com .. load_user_{N-1}@example.com (role=user)

Re-runs are safe: existing emails are skipped (ON CONFLICT DO NOTHING).
Use --clear to delete previous load_* users before inserting.
"""

from __future__ import annotations

import argparse
import asyncio
import time
from uuid import uuid4

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.enums import UserRoles
from app.services.auth_service import AuthService
from app.storage.postgresql.connection import DatabaseManager
from app.storage.postgresql.models.user_model import UserOrm

ADMIN_EMAIL = "load_admin@example.com"
USER_EMAIL_TEMPLATE = "load_user_{i}@example.com"
DEFAULT_PASSWORD = "password"
DEFAULT_COUNT = 100000
DEFAULT_BATCH_SIZE = 1000


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed users into the database")
    parser.add_argument("--count", type=int, default=DEFAULT_COUNT)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--password", type=str, default=DEFAULT_PASSWORD)
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Delete load_admin and load_user_* rows before seeding",
    )
    return parser.parse_args()


def _user_row(
    *,
    first_name: str,
    last_name: str,
    email: str,
    hashed_password: str,
    role: UserRoles,
) -> dict:
    return {
        "id": uuid4(),
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "hashed_password": hashed_password,
        "role": role,
        "active": True,
    }


async def _insert_batch(rows: list[dict]) -> None:
    async with DatabaseManager.session_factory() as session:
        stmt = (
            pg_insert(UserOrm)
            .values(rows)
            .on_conflict_do_nothing(index_elements=["email"])
        )
        await session.execute(stmt)
        await session.commit()


async def _clear_load_users() -> int:
    async with DatabaseManager.session_factory() as session:
        result = await session.execute(
            delete(UserOrm).where(
                (UserOrm.email == ADMIN_EMAIL)
                | UserOrm.email.startswith("load_user_")
            )
        )
        await session.commit()
        return result.rowcount or 0


async def seed(count: int, batch_size: int, password: str, clear: bool) -> None:
    if count < 1:
        raise ValueError("--count must be >= 1")
    if batch_size < 1:
        raise ValueError("--batch-size must be >= 1")

    # if clear:
    #     deleted = await _clear_load_users()
    #     print(f"Cleared {deleted} previous load users")

    hashed_password = AuthService.hash_password(password).decode("utf-8")
    started = time.perf_counter()

    admin_row = _user_row(
        first_name="Load",
        last_name="Admin",
        email=ADMIN_EMAIL,
        hashed_password=hashed_password,
        role=UserRoles.admin,
    )
    await _insert_batch([admin_row])
    print(f"Admin ready: {ADMIN_EMAIL} / {password}")

    for start in range(0, count, batch_size):
        end = min(start + batch_size, count)
        rows = [
            _user_row(
                first_name="Load",
                last_name=f"User{i}",
                email=USER_EMAIL_TEMPLATE.format(i=i),
                hashed_password=hashed_password,
                role=UserRoles.user,
            )
            for i in range(start, end)
        ]
        await _insert_batch(rows)
        elapsed = time.perf_counter() - started
        print(f"Inserted batch {start}:{end} ({end}/{count}) in {elapsed:.1f}s")

    total = time.perf_counter() - started
    print(
        f"Done. Seeded up to {count} users (+ admin) in {total:.1f}s. "
        f"Plain password for all: {password}"
    )


def main() -> None:
    args = _parse_args()
    asyncio.run(seed(args.count, args.batch_size, args.password, args.clear))


if __name__ == "__main__":
    main()
