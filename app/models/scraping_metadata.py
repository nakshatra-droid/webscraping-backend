from datetime import datetime
from sqlalchemy import Uuid, Integer, Boolean, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base


class ScrapingMetadata(Base):
    __tablename__ = "scraping_metadata"

    id: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        nullable=False,
        index=True,
    )
    total_products_attempted: Mapped[int] = mapped_column(
        Integer, default=0, nullable=True
    )
    valid_products: Mapped[int] = mapped_column(Integer, default=0, nullable=True)
    invalid_products: Mapped[int] = mapped_column(Integer, default=0, nullable=True)
    start_time: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    is_fallback_run: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # relationships
    product_details = relationship("ProductDetails", back_populates="scraping_metadata")
    activity_logs = relationship("ActivityLogs", back_populates="scraping_metadata")
