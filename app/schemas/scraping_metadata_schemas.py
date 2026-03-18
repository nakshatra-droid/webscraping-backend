from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class ScrapingMetadataBase(BaseModel):
    total_products_attempted: Optional[int] = 0
    valid_products: Optional[int] = 0
    invalid_products: Optional[int] = 0
    start_time: datetime = Field(..., description="When the scraping run started")
    end_time: Optional[datetime] = None
    is_fallback_run: Optional[bool] = False


class ScrapingMetadataResponse(ScrapingMetadataBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
