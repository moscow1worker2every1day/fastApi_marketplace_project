import factory
from app.storage.postgresql.models.user_model import UserOrm

class UserFactory(factory.Factory):
    class Meta:
        model = UserOrm

    id = factory.Sequence(lambda n: n + 1)
    first_name = "Anast"
    last_name = "Marti"
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    active = True
    role = "user"
    updated_at = "2026-02-19T10:49:45.062194"
    created_at = "2026-02-19T10:49:45.062194"
    hashed_password = "$2b$12$TEgDpGP4JXo5yTQkuDHF.e8iLu.Z4dINLqpP3ELm2rMzJzyGUcEom"