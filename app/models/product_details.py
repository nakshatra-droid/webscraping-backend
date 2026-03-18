from datetime import datetime
from sqlalchemy import (
    ForeignKey,
    UniqueConstraint,
    Uuid,
    Text,
    Numeric,
    Integer,
    func,
    DateTime,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base
from app.models.enums import listing_source_enum


class ProductDetails(Base):
    __tablename__ = "product_details"
    __table_args__ = (
        UniqueConstraint(
            "product_id", "source", name="product_details_product_id_source_key"
        ),
    )
    id: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=func.gen_random_uuid(),
        nullable=False,
        index=True,
    )
    product_id: Mapped[Uuid] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    source: Mapped[str] = mapped_column(listing_source_enum, nullable=False)
    run_id: Mapped[Uuid] = mapped_column(
        ForeignKey("scraping_metadata.id"), nullable=True
    )
    price: Mapped[float] = mapped_column(Numeric, nullable=True)
    discount: Mapped[int] = mapped_column(Integer, nullable=True)
    rating: Mapped[float] = mapped_column(Numeric(2, 1), nullable=True)
    review_count: Mapped[int] = mapped_column(Integer, nullable=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str] = mapped_column(Text, nullable=True)

    scraped_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # relationships
    products = relationship("Products", back_populates="product_details")
    scraping_metadata = relationship(
        "ScrapingMetadata", back_populates="product_details"
    )
