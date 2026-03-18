from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.middleware.auth import AuthMiddleware
from app.models.users import Users
from app.schemas.common_schemas import MessageResponse, PaginatedResponse
from app.database.database import get_db
from app.services.embedding_metadata_service import EmbeddingMetadataService
from app.schemas.embedding_metadata_schemas import EmbeddingMetadataResponse
from app.constants.constants import PaginationConstants

router = APIRouter()


@router.get(
    path="/metadata",
    response_model=PaginatedResponse[EmbeddingMetadataResponse],
    summary="Get All Embedding Metadata (Admin)",
    description="Retrieve all embedding pipeline runs with pagination - Admin only",
    responses={
        200: {"description": "Embedding metadata retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
    },
)
async def get_all_embedding_metadata(
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
) -> PaginatedResponse[EmbeddingMetadataResponse]:
    """Get all embedding metadata runs - Admin only"""
    service = EmbeddingMetadataService(db)
    result = await service.get_all_embedding_metadata(page=page, size=size)
    return PaginatedResponse[EmbeddingMetadataResponse](**result)


@router.post(
    path="/run",
    response_model=MessageResponse,
    summary="Trigger Embedding Pipeline (Admin)",
    description="Manually trigger the embedding generation pipeline. ",
    responses={
        200: {"description": "Embedding task started successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
    },
)
async def trigger_embedding_run(
    current_user: Users = Depends(AuthMiddleware.get_current_admin),
) -> MessageResponse:
    """Placeholder to trigger the Airflow embedding DAG."""
    return MessageResponse(
        message="Embedding trigger accepted",
        data={"status": "queued"},
    )
