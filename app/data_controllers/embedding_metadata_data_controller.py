from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any
from app.models.embedding_metadata import EmbeddingMetadata
import math


class EmbeddingMetadataDataController:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_embedding_metadata(
        self, page: int = 1, size: int = 10
    ) -> Dict[str, Any]:
        """Get all embedding metadata runs with pagination."""
        skip = (page - 1) * size

        total_result = await self.db.execute(select(func.count(EmbeddingMetadata.id)))
        total = total_result.scalar()

        result = await self.db.execute(
            select(EmbeddingMetadata)
            .order_by(EmbeddingMetadata.created_at.desc())
            .offset(skip)
            .limit(size)
        )
        data = result.scalars().all()

        pages = math.ceil(total / size) if total > 0 else 0

        return {
            "total": total,
            "page": page,
            "size": size,
            "pages": pages,
            "data": data,
        }
