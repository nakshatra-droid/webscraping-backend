from datetime import datetime
from sqlalchemy import Uuid, Text, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base
from app.models.enums import embedding_status_enum
from app.constants.constants import EmbeddingStatus


class Products(Base):
    __tablename__ = "products"

    id: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=func.gen_random_uuid(),
        nullable=False,
        index=True,
    )
    model_number: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    brand: Mapped[str] = mapped_column(Text, nullable=True)
    series: Mapped[str] = mapped_column(Text, nullable=True)
    processor: Mapped[str] = mapped_column(Text, nullable=True)
    ram: Mapped[str] = mapped_column(Text, nullable=True)
    storage: Mapped[str] = mapped_column(Text, nullable=True)
    screen_size: Mapped[str] = mapped_column(Text, nullable=True)
    graphic_processor: Mapped[str] = mapped_column(Text, nullable=True)
    colour: Mapped[str] = mapped_column(Text, nullable=True)

    embedding_status: Mapped[str] = mapped_column(
        embedding_status_enum,
        default=EmbeddingStatus.PENDING,
        nullable=False,
    )
    embedded_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # relationships
    product_details = relationship("ProductDetails", back_populates="products")
    product_embeddings = relationship(
        "ProductEmbeddings",
        back_populates="products",
        cascade="all, delete-orphan",
    )
