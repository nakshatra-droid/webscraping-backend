from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.schemas.product_schemas import (
    ProductCreate,
    ProductListingUpdate,
    ProductSummaryResponse,
    AdminProductResponse,
    CompareRequest,
)
from app.schemas.common_schemas import MessageResponse, PaginatedResponse
from app.services.products_service import ProductsService
from app.middleware.auth import AuthMiddleware
from app.models.users import Users
from uuid import UUID
from app.constants.constants import PaginationConstants

router = APIRouter()


# User endpoints
@router.get(
    path="/",
    response_model=PaginatedResponse[ProductSummaryResponse],
    summary="Get Products",
    description="Retrieve products with summary pricing",
    responses={
        200: {"description": "Products retrieved successfully"},
        401: {"description": "Unauthorized"},
    },
)
async def get_products(
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
    search: Optional[str] = Query(
        default=None,
        description="Search by model number, brand, series, or processor",
    ),
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(AuthMiddleware.get_current_user),
) -> PaginatedResponse[ProductSummaryResponse]:
    """Get products for the current user"""

    service = ProductsService(db)
    result = await service.get_products(page=page, size=size, search=search)
    return PaginatedResponse[ProductSummaryResponse](**result)


@router.get(
    path="/compare",
    response_model=MessageResponse,
    summary="Compare Products",
    description="Compare products by ID",
    responses={
        200: {"description": "Comparison retrieved successfully"},
        401: {"description": "Unauthorized"},
    },
)
async def compare_products_query(
    ids: str = Query(..., description="Comma-separated product IDs"),
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(AuthMiddleware.get_current_user),
) -> MessageResponse:
    """Compare products by query string"""

    try:
        id_list = [UUID(pid.strip()) for pid in ids.split(",") if pid.strip()]
    except ValueError:
        return MessageResponse(
            message="Invalid product IDs",
            data=[],
        )
    service = ProductsService(db)
    products = await service.get_products_by_ids(id_list)
    return MessageResponse(
        message="Comparison retrieved successfully",
        data=[p.model_dump() for p in products],
    )


@router.post(
    path="/compare",
    response_model=MessageResponse,
    summary="Compare Products (POST)",
    description="Compare products by ID list",
    responses={
        200: {"description": "Comparison retrieved successfully"},
        401: {"description": "Unauthorized"},
    },
)
async def compare_products_body(
    payload: CompareRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(AuthMiddleware.get_current_user),
) -> MessageResponse:
    """Compare products by request body"""

    service = ProductsService(db)
    products = await service.get_products_by_ids(payload.product_ids)
    return MessageResponse(
        message="Comparison retrieved successfully",
        data=[p.model_dump() for p in products],
    )


@router.get(
    path="/{product_id}",
    response_model=MessageResponse,
    summary="Get Product by ID",
    description="Retrieve a specific product with listings by ID",
    responses={
        200: {"description": "Product retrieved successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Product not found"},
    },
)
async def get_product_by_id(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(AuthMiddleware.get_current_user),
) -> MessageResponse:
    """Get a specific product by ID"""

    service = ProductsService(db)
    product = await service.get_product_by_id(product_id)
    return MessageResponse(
        message="Product retrieved successfully",
        data=product.model_dump(),
    )


# Admin endpoints
admin_router = APIRouter()


@admin_router.get(
    path="/",
    response_model=PaginatedResponse[AdminProductResponse],
    summary="Get All Products (Admin)",
    description="Retrieve all products - Admin only",
    responses={
        200: {"description": "All products retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
    },
)
async def get_all_products_admin(
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
    search: Optional[str] = Query(
        default=None,
        description="Search by model number, brand, series, or processor",
    ),
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(AuthMiddleware.get_current_admin),
) -> PaginatedResponse[AdminProductResponse]:
    """Get all products - Admin only"""

    service = ProductsService(db)
    result = await service.get_all_products_admin(page=page, size=size, search=search)
    return PaginatedResponse[AdminProductResponse](**result)


@admin_router.get(
    path="/{id}",
    response_model=MessageResponse,
    summary="Get Product with Listings (Admin)",
    description="Retrieve a product with listings by ID - Admin only",
    responses={
        200: {"description": "Product retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Product not found"},
    },
)
async def get_product_with_details_admin(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(AuthMiddleware.get_current_admin),
) -> MessageResponse:
    """Retrieve a product with listings by ID - Admin only"""

    service = ProductsService(db)
    product = await service.get_product_with_details_admin(id)
    return MessageResponse(
        message="Product retrieved successfully",
        data=product.model_dump(),
    )


@admin_router.post(
    path="/",
    response_model=MessageResponse,
    summary="Create Product Entry (Admin)",
    description="Create a new product entry with listing - Admin only",
    responses={
        200: {"description": "Product entry created successfully"},
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
    },
)
async def create_product_entry(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(AuthMiddleware.get_current_admin),
) -> MessageResponse:
    """Create a new product entry with listing - Admin only"""

    service = ProductsService(db)
    product = await service.create_product_with_detail(product_data)
    return MessageResponse(
        message="Product entry created successfully", data=product.model_dump()
    )


@admin_router.put(
    path="/{product_id}/{source}",
    response_model=MessageResponse,
    summary="Update Product Listing (Admin)",
    description="Update product listing for a specific source - Admin only",
    responses={
        200: {"description": "Product listing updated successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Listing not found"},
    },
)
async def update_product_detail(
    product_id: UUID,
    source: str,
    update_data: ProductListingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(AuthMiddleware.get_current_admin),
) -> MessageResponse:
    """Update product listing for a specific source - Admin only"""

    service = ProductsService(db)
    product = await service.update_product_detail(product_id, source, update_data)
    return MessageResponse(
        message="Product listing updated successfully", data=product.model_dump()
    )


@admin_router.delete(
    path="/{id}",
    response_model=MessageResponse,
    summary="Delete Product (Admin)",
    description="Delete a product and all its listings - Admin only",
    responses={
        200: {"description": "Product deleted successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Product not found"},
    },
)
async def delete_product(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(AuthMiddleware.get_current_admin),
) -> MessageResponse:
    """Delete a product and all its listings - Admin only"""

    service = ProductsService(db)
    await service.delete_product(id)
    return MessageResponse(message="Product deleted successfully")


@admin_router.delete(
    path="/{product_id}/{source}",
    response_model=MessageResponse,
    summary="Delete Product Listing (Admin)",
    description="Delete product listing for a specific source - Admin only",
    responses={
        200: {"description": "Product listing deleted successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Listing not found"},
    },
)
async def delete_product_detail(
    product_id: UUID,
    source: str,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(AuthMiddleware.get_current_admin),
) -> MessageResponse:
    """Delete a product listing for a specific source - Admin only"""

    service = ProductsService(db)
    await service.delete_product_detail(product_id, source)
    return MessageResponse(message="Product listing deleted successfully")
