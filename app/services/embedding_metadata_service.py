from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from app.data_controllers.embedding_metadata_data_controller import (
    EmbeddingMetadataDataController,
)
from app.schemas.embedding_metadata_schemas import EmbeddingMetadataResponse


class EmbeddingMetadataService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.controller = EmbeddingMetadataDataController(db)

    async def get_all_embedding_metadata(
        self, page: int = 1, size: int = 10
    ) -> Dict[str, Any]:
        """Get all embedding metadata runs with pagination."""
        result = await self.controller.get_all_embedding_metadata(page=page, size=size)
        result["data"] = [
            EmbeddingMetadataResponse.model_validate(run) for run in result["data"]
        ]
        return result
