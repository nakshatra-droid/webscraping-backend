from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.schemas.scraping_metadata_schemas import ScrapingMetadataResponse
from app.services.scraping_metadata_service import ScrapingMetadataService
from app.middleware.auth import AuthMiddleware
from app.models.users import Users
from app.constants.constants import PaginationConstants
from app.schemas.common_schemas import MessageResponse, PaginatedResponse

router = APIRouter()


@router.get(
    path="/",
    response_model=PaginatedResponse[ScrapingMetadataResponse],
    summary="Get All Scraping Runs",
    description="Retrieve all scraping runs metadata - Admin only",
    responses={
        200: {"description": "Scraping runs retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
    },
)
async def get_all_scraping_runs(
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
) -> PaginatedResponse[ScrapingMetadataResponse]:
    """Get metadata for all scraping runs - Admin only"""

    service = ScrapingMetadataService(db)
    result = await service.get_all_scraping_runs(page=page, size=size)
    return PaginatedResponse[ScrapingMetadataResponse](**result)


@router.post(
    path="/run",
    response_model=MessageResponse,
    summary="Trigger Scraping Run (Admin)",
    description="Dummy endpoint to trigger the Airflow scraping DAG in the future.",
    responses={
        200: {"description": "Scraping trigger accepted"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
    },
)
async def trigger_scraping_run(
    current_user: Users = Depends(AuthMiddleware.get_current_admin),
) -> MessageResponse:
    """Placeholder to trigger Airflow scraping DAG."""

    return MessageResponse(
        message="Scraping trigger accepted", data={"status": "queued"}
    )
