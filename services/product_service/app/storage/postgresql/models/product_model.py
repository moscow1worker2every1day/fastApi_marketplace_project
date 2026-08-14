from sqlalchemy import String, CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.storage.postgresql.models.base_model import Base
import uuid


class ProductOrm(Base):

    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=lambda: uuid.uuid4(),
    )
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(1024))
    price: Mapped[float]
    stock: Mapped[int]
    available: Mapped[bool] = mapped_column(
        server_default="true",
        default=True,
    )
    seller_id: Mapped[uuid.UUID]

    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False,
    )

    category: Mapped["CategoryOrm"] = relationship(
        back_populates="products",
    )

    __table_args__ = (
        CheckConstraint("price >= 0", name="check_product_price_positive"),
        CheckConstraint("stock >= 0", name="check_product_stock_positive"),
    )
