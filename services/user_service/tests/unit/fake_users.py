from uuid import uuid4
from datetime import datetime, timezone

import factory
from app.storage.postgresql.models.user_model import UserOrm
from app.enums import UserRoles


class UserFactory(factory.Factory):
    class Meta:
        model = UserOrm

    id = factory.LazyFunction(uuid4)
    first_name = "Test"
    last_name = "User Boy"
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    active = True
    role = UserRoles.user
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    hashed_password = "$2b$12$TEgDpGP4JXo5yTQkuDHF.e8iLu.Z4dINLqpP3ELm2rMzJzyGUcEom"
