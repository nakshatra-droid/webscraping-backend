from fastapi import APIRouter, Depends
from app.services.dashboard_service import DashboardService
from app.database.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.dashboard_stats_schema import DashboardStatsSchema
from app.schemas.common_schemas import MessageResponse
from app.middleware.auth import AuthMiddleware
from app.models.users import Users

router = APIRouter()


@router.get("/stats", response_model=MessageResponse)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(AuthMiddleware.get_current_admin),
):
    stats = await DashboardService(db).get_stats()
    return MessageResponse(
        message="Dashboard stats fetched successfully",
        data=DashboardStatsSchema(**stats).dict(),
    )
