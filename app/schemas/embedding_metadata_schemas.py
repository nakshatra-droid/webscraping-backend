from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class EmbeddingMetadataBase(BaseModel):
    model_name: str
    total_attempted: int
    success_count: int
    failed_count: int
    status: str
    start_time: datetime
    end_time: datetime | None = None
    created_at: datetime
    updated_at: datetime


class EmbeddingMetadataResponse(EmbeddingMetadataBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
