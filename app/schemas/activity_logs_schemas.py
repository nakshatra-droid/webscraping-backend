from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any


class ActivityLogBase(BaseModel):
    run_id: Optional[UUID] = None
    activity_type: str = Field(..., description="Type of activity")
    product_data: Optional[Dict[str, Any]] = None
    product_url: str = Field(..., description="URL of the product")
    retry_count: Optional[int] = 0
    human_review_flag: Optional[bool] = False


class ActivityLogUpdate(BaseModel):
    retry_count: Optional[int] = Field(
        None, ge=0, le=3, description="Retry count must be between 0 and 3"
    )
    human_review_flag: Optional[bool] = None


class ActivityLogResponse(ActivityLogBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
