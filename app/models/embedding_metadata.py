from datetime import datetime
from sqlalchemy import Uuid, String, Integer, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base


class EmbeddingMetadata(Base):
    __tablename__ = "embedding_metadata"

    id: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=func.gen_random_uuid(),
        nullable=False,
        index=True,
    )
    model_name: Mapped[str] = mapped_column(String, nullable=False)
    total_attempted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    success_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    start_time: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # relationships
    product_embeddings = relationship(
        "ProductEmbeddings",
        back_populates="embedding_metadata",
    )
