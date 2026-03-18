from sqlalchemy.ext.asyncio import AsyncSession
from app.data_controllers.scraping_metadata_data_controller import (
    ScrapingMetadataDataController,
)
from app.schemas.scraping_metadata_schemas import (
    ScrapingMetadataResponse,
)
from typing import Dict, Any


class ScrapingMetadataService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.controller = ScrapingMetadataDataController(db)

    async def get_all_scraping_runs(
        self, page: int = 1, size: int = 10
    ) -> Dict[str, Any]:
        """Get all scraping runs - Admin only"""

        result = await self.controller.get_all_scraping_runs(page=page, size=size)
        result["data"] = [
            ScrapingMetadataResponse.model_validate(run) for run in result["data"]
        ]
        return result
