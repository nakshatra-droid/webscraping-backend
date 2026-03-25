from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.middleware.auth import AuthMiddleware
from app.models.users import Users
from app.schemas.common_schemas import MessageResponse, PaginatedResponse
from app.database.database import get_db
from app.services.embedding_metadata_service import EmbeddingMetadataService
from app.services.airflow_service import AirflowService
from app.schemas.embedding_metadata_schemas import EmbeddingMetadataResponse
from app.schemas.airflow_schemas import EmbeddingDagTriggerRequest
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
    payload: Optional[EmbeddingDagTriggerRequest] = None,
    current_user: Users = Depends(AuthMiddleware.get_current_admin),
) -> MessageResponse:
    """Trigger the Airflow embedding DAG."""

    service = AirflowService()
    payload = payload or EmbeddingDagTriggerRequest()
    data = await service.trigger_embedding_run(
        dag_id=payload.dag_id,
        extra_conf=payload.conf,
    )

    return MessageResponse(
        message="Embedding DAG triggered",
        data=data,
    )
