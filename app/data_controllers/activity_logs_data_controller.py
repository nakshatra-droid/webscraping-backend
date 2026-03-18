from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from typing import Optional, Dict, Any
from uuid import UUID
from app.models.activity_logs import ActivityLogs
from app.schemas.activity_logs_schemas import ActivityLogUpdate
import math


class ActivityLogsDataController:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_activity_logs(
        self, page: int = 1, size: int = 10
    ) -> Dict[str, Any]:
        """Get all activity logs - Admin only"""

        skip = (page - 1) * size

        # Get total count
        total_result = await self.db.execute(
            select(func.count(ActivityLogs.id)).where(ActivityLogs.deleted_at.is_(None))
        )
        total = total_result.scalar()

        # Get paginated data
        result = await self.db.execute(
            select(ActivityLogs)
            .where(ActivityLogs.deleted_at.is_(None))
            .order_by(ActivityLogs.created_at.desc())
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

    async def get_activity_log_by_id(self, log_id: UUID) -> Optional[ActivityLogs]:
        """Get an activity log by its ID - Admin only"""

        result = await self.db.execute(
            select(ActivityLogs).where(
                ActivityLogs.id == log_id, ActivityLogs.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    async def update_activity_log(
        self, log_id: UUID, update_data: ActivityLogUpdate
    ) -> Optional[ActivityLogs]:
        """Update an activity log - Admin only"""
        try:
            update_dict = update_data.model_dump(exclude_unset=True)

            result = await self.db.execute(
                update(ActivityLogs)
                .where(ActivityLogs.id == log_id, ActivityLogs.deleted_at.is_(None))
                .values(**update_dict)
                .returning(ActivityLogs)
            )
            log = result.scalar_one_or_none()
            if not log:
                await self.db.rollback()
                return None
            else:
                await self.db.commit()
                return log
        except Exception:
            await self.db.rollback()
            raise
