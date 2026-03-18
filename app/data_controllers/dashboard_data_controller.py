from typing import Dict, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.products import Products
from app.models.users import Users
from app.models.activity_logs import ActivityLogs
from app.models.scraping_metadata import ScrapingMetadata
from app.models.embedding_metadata import EmbeddingMetadata
from app.models.product_embeddings import ProductEmbeddings
from app.constants.constants import ActivityTypes


class DashboardDataController:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_stats(self) -> Dict:
        """
        Get all the stats for the dashboard
        """
        # Get ALL counts in a single query
        all_counts = await self._get_all_counts()

        # Get grouped stats
        grouped_stats = await self._get_grouped_stats()

        return {
            **all_counts,
            **grouped_stats,
        }

    async def _get_all_counts(self) -> Dict:
        """
        Get all simple counts and product detail stats in one query
        """
        query = select(
            # Simple table counts
            select(func.count())
            .select_from(Products)
            .scalar_subquery()
            .label("total_products"),
            select(func.count())
            .select_from(Users)
            .scalar_subquery()
            .label("total_users"),
            select(func.count())
            .select_from(ScrapingMetadata)
            .scalar_subquery()
            .label("total_scraper_runs"),
            select(func.count())
            .select_from(ActivityLogs)
            .scalar_subquery()
            .label("total_activity_logs"),
            select(func.count())
            .select_from(EmbeddingMetadata)
            .scalar_subquery()
            .label("total_embedding_runs"),
            select(func.count())
            .select_from(ProductEmbeddings)
            .scalar_subquery()
            .label("total_embeddings"),
        )

        result = (await self.db.execute(query)).first()

        return {
            "total_products": int(result.total_products or 0),
            "total_users": int(result.total_users or 0),
            "total_scraper_runs": int(result.total_scraper_runs or 0),
            "total_activity_logs": int(result.total_activity_logs or 0),
            "total_embedding_runs": int(result.total_embedding_runs or 0),
            "total_embeddings": int(result.total_embeddings or 0),
        }

    async def _get_grouped_stats(self) -> Dict:
        """Get grouped statistics - 2 queries"""
        # Activity types
        activity_results = await self._get_grouped_counts(
            ActivityLogs, ActivityLogs.activity_type
        )

        act_types = [
            ActivityTypes.REDIRECTED,
            ActivityTypes.PRODUCT_NOT_FOUND,
            ActivityTypes.FIELD_MISSING,
            ActivityTypes.ALREADY_EXIST,
        ]
        activity_types_dict = dict(activity_results)
        activity_types = {act: activity_types_dict.get(act, 0) for act in act_types}

        return {
            "activity_types": activity_types,
        }

    async def _get_grouped_counts(self, model, column) -> List[Tuple]:
        """Get grouped counts for a specific column"""
        query = select(column, func.count()).group_by(column)
        result = await self.db.execute(query)
        return result.all()
