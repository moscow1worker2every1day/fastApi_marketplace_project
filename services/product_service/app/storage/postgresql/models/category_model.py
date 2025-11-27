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
from typing import List
from app.storage.postgresql.models.base_model import Base

from app.storage.postgresql.models.product_model import ProductOrm

class CategoryOrm(Base):

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(1024), nullable=False, default="Нет описания")

    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True
    )

    parent: Mapped["CategoryOrm"] = relationship(remote_side=[id], back_populates="children")

    children: Mapped[List["CategoryOrm"]] = relationship(back_populates="parent")

    products: Mapped[List["ProductOrm"]] = relationship(
        back_populates="category"
    )

