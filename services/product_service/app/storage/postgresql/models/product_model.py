from sqlalchemy import String, Float, Boolean, Integer, CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.storage.postgresql.models.base_model import Base


class ProductOrm(Base):

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(1024), nullable=False, default="Нет описания")
    price: Mapped[float] = mapped_column(Float, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)
    available: Mapped[bool] = mapped_column(Boolean, default=True)

    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"))

    category: Mapped["CategoryOrm"] = relationship(back_populates="products")

    __table_args__ = (
        CheckConstraint("price >= 0", name="check_product_price_positive"),
        CheckConstraint("stock >= 0", name="check_product_stock_positive")
    )
