import uuid
from sqlalchemy import String, func, Enum, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from app.storage.postgresql.models.base_model import Base
from app.enums import UserRoles


class UserOrm(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True
    )
    first_name: Mapped[str] = mapped_column(
        String(64),
    )
    last_name: Mapped[str] = mapped_column(
        String(64),    
    )
    email: Mapped[str] = mapped_column(
        String,
        unique=True,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(),
    )
    role: Mapped[UserRoles] = mapped_column(
        Enum(UserRoles, name="user_role"),
        server_default=UserRoles.user.value
    )
    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        onupdate=func.now(),
        server_default=func.now()
    )
