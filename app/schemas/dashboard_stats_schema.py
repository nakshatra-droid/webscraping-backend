from pydantic import BaseModel, Field
from typing import Dict, Optional


class DashboardStatsSchema(BaseModel):
    total_products: int = Field(...)
    total_users: int = Field(...)
    total_scraper_runs: int = Field(...)
    total_activity_logs: int = Field(...)
    total_embedding_runs: int = Field(...)
    total_embeddings: int = Field(...)
    activity_types: Dict[str, int] = Field(default_factory=dict)
