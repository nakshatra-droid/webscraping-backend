from sqlalchemy.ext.asyncio import AsyncSession
from app.data_controllers.activity_logs_data_controller import (
    ActivityLogsDataController,
)
from app.schemas.activity_logs_schemas import ActivityLogUpdate, ActivityLogResponse
from typing import Dict, Any
from uuid import UUID
from app.exceptions import NotFoundException, ValidationException


class ActivityLogsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.controller = ActivityLogsDataController(db)

    async def get_all_activity_logs(
        self, page: int = 1, size: int = 10
    ) -> Dict[str, Any]:
        """Get all activity logs - Admin only"""

        result = await self.controller.get_all_activity_logs(page=page, size=size)
        result["data"] = [
            ActivityLogResponse.model_validate(log) for log in result["data"]
        ]
        return result

    async def get_activity_log_by_id(self, log_id: UUID) -> ActivityLogResponse:
        """Get a specific activity log by its ID - Admin only"""

        log = await self.controller.get_activity_log_by_id(log_id)
        if not log:
            raise NotFoundException("Activity log not found")
        return ActivityLogResponse.model_validate(log)

    async def update_activity_log(
        self, log_id: UUID, update_data: ActivityLogUpdate
    ) -> ActivityLogResponse:
        """Update an existing activity log - Admin only"""

        update_dict = update_data.model_dump(exclude_unset=True)
        if not update_dict:
            raise ValidationException("No fields provided for update")

        log = await self.controller.update_activity_log(log_id, update_data)

        if not log:
            raise NotFoundException("Activity log not found for this ID")
        return ActivityLogResponse.model_validate(log)
