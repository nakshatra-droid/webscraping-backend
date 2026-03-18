from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Index, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from app.database.database import Base


class ProductEmbeddings(Base):
    __tablename__ = "product_embeddings"
    __table_args__ = (
        Index(
            "product_embeddings_embedding_hnsw_idx",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
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

    embedding_metadata_id: Mapped[Uuid] = mapped_column(
        ForeignKey("embedding_metadata.id", ondelete="SET NULL"), nullable=True
    )

    embedding = mapped_column(Vector(768), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # relationships
    products = relationship(
        "Products", foreign_keys=[product_id], back_populates="product_embeddings"
    )
    embedding_metadata = relationship(
        "EmbeddingMetadata",
        foreign_keys=[embedding_metadata_id],
        back_populates="product_embeddings",
    )
