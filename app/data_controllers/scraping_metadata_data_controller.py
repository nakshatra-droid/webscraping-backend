from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any
from app.models.scraping_metadata import ScrapingMetadata
import math


class ScrapingMetadataDataController:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_scraping_runs(
        self, page: int = 1, size: int = 10
    ) -> Dict[str, Any]:
        """Get all scraping runs - Admin only"""

        skip = (page - 1) * size

        # Get total count
        total_result = await self.db.execute(
            select(func.count(ScrapingMetadata.id)).where(
                ScrapingMetadata.deleted_at.is_(None)
            )
        )
        total = total_result.scalar()

        # Get paginated data
        result = await self.db.execute(
            select(ScrapingMetadata)
            .where(ScrapingMetadata.deleted_at.is_(None))
            .order_by(ScrapingMetadata.created_at.desc())
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
