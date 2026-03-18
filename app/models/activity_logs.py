from datetime import datetime
from sqlalchemy import ForeignKey, Uuid, Text, Integer, Boolean, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base
from sqlalchemy.dialects.postgresql import JSONB
from app.models.enums import activity_type_enum


class ActivityLogs(Base):
    __tablename__ = "activity_logs"

    id: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=func.gen_random_uuid(),
        nullable=False,
        index=True,
    )
    run_id: Mapped[Uuid] = mapped_column(
        ForeignKey("scraping_metadata.id"), nullable=True
    )
    activity_type: Mapped[str] = mapped_column(activity_type_enum, nullable=False)
    product_data: Mapped[dict] = mapped_column(JSONB, nullable=True)
    product_url: Mapped[str] = mapped_column(Text, nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=True)
    human_review_flag: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # relationships
    scraping_metadata = relationship("ScrapingMetadata", back_populates="activity_logs")
