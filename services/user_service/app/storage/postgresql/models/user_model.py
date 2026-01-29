from sqlalchemy import String, func, Enum, Boolean, Integer, Date
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.storage.postgresql.models.base_model import Base
from app.config import UserRoles


class UserOrm(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    last_name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRoles] = mapped_column(Enum(UserRoles, name="user_role"), server_default=UserRoles.user.value)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(onupdate=func.now(), insert_default=func.now())
