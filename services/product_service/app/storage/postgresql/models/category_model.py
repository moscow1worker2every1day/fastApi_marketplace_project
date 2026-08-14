'''
result = await session.scalars(
    select(Category)
    .options(selectinload(Category.children))
    .options(selectinload(Category.products))
)
categories = result.all()
'''

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.storage.postgresql.models.base_model import Base
import uuid

class CategoryOrm(Base):

    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=lambda: uuid.uuid4()
    )
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        String(1024),
        nullable=True,
        default=None,
    )

    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        server_default=None,
    )

    parent: Mapped["CategoryOrm"] = relationship(
        remote_side=[id],
        back_populates="children",
    )
    children: Mapped[list["CategoryOrm"]] = relationship(
        back_populates="parent",
    )
    products: Mapped[list["ProductOrm"]] = relationship(
        back_populates="category",
    )
