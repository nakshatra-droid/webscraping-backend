from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.schemas.activity_logs_schemas import ActivityLogUpdate, ActivityLogResponse
from app.schemas.common_schemas import MessageResponse, PaginatedResponse
from app.services.activity_logs_service import ActivityLogsService
from app.middleware.auth import AuthMiddleware
from app.models.users import Users
from uuid import UUID
from app.constants.constants import PaginationConstants

router = APIRouter()


@router.get(
    path="/",
    response_model=PaginatedResponse[ActivityLogResponse],
    summary="Get All Activity Logs",
    description="Retrieve all activity logs - Admin only",
    responses={
        200: {"description": "Activity logs retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
    },
)
async def get_all_activity_logs(
    page: int = Query(
        default=PaginationConstants.DEFAULT_PAGE,
        ge=1,
        description="Page number, starting from 1",
    ),
    size: int = Query(
        default=PaginationConstants.DEFAULT_SIZE,
        ge=1,
        le=PaginationConstants.MAX_SIZE,
        description="Number of items per page",
    ),
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(AuthMiddleware.get_current_admin),
) -> PaginatedResponse[ActivityLogResponse]:
    """Retrieve all activity logs - Admin only"""

    service = ActivityLogsService(db)
    result = await service.get_all_activity_logs(page=page, size=size)
    return PaginatedResponse[ActivityLogResponse](**result)


@router.get(
    path="/{log_id}",
    response_model=MessageResponse,
    summary="Get Activity Log by ID",
    description="Retrieve a specific activity log by its ID - Admin only",
    responses={
        200: {"description": "Activity log retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Log not found"},
    },
)
async def get_activity_log_by_id(
    log_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(AuthMiddleware.get_current_admin),
) -> MessageResponse:
    """Get a specific activity log by its ID - Admin only"""

    service = ActivityLogsService(db)
    log = await service.get_activity_log_by_id(log_id)
    return MessageResponse(
        message="Activity log retrieved successfully", data=log.model_dump()
    )


@router.put(
    path="/{log_id}",
    response_model=MessageResponse,
    summary="Update Activity Log",
    description="Update an existing activity log - Admin only",
    responses={
        200: {"description": "Activity log updated successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Log not found"},
    },
)
async def update_activity_log(
    log_id: UUID,
    log_update: ActivityLogUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(AuthMiddleware.get_current_admin),
) -> MessageResponse:
    """Update an existing activity log - Admin only"""

    service = ActivityLogsService(db)
    updated_log = await service.update_activity_log(log_id, log_update)
    return MessageResponse(
        message="Activity log updated successfully", data=updated_log.model_dump()
    )
