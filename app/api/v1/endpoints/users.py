from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.schemas.user_schemas import (
    UserCreate,
    UserUpdate,
    ChangePasswordRequest,
    UserResponse,
)
from app.schemas.common_schemas import MessageResponse, PaginatedResponse
from app.services.user_service import UserService
from app.middleware.auth import AuthMiddleware
from app.models.users import Users
from uuid import UUID
from app.constants.constants import PaginationConstants

router = APIRouter()


@router.get(path="/", response_model=PaginatedResponse[UserResponse])
async def read_all_users(
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
) -> PaginatedResponse[UserResponse]:
    """Get all the users in the system - Admin only"""

    user_service = UserService(db)
    result = await user_service.get_all_users(page=page, size=size)
    return PaginatedResponse[UserResponse](**result)


@router.post(
    path="/",
    response_model=MessageResponse,
    summary="Create New User",
    description="Create a new user account - Admin only",
    responses={
        200: {"description": "User created successfully"},
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
    },
)
async def create_new_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(AuthMiddleware.get_current_admin),
) -> MessageResponse:
    """Create a new user account - Admin only"""

    user_service = UserService(db)
    new_user = await user_service.create_user(user)
    return MessageResponse(
        message="User created successfully", data=new_user.model_dump()
    )


@router.get(
    path="/{user_id}",
    response_model=MessageResponse,
    summary="Get User by ID",
    description="Retrieve a specific user by ID - Admin only",
    responses={
        200: {"description": "User retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "User not found"},
    },
)
async def read_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(AuthMiddleware.get_current_admin),
) -> MessageResponse:
    """Retrieve a specific user by ID - Admin only"""

    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    return MessageResponse(
        message="User retrieved successfully", data=user.model_dump()
    )


@router.put(
    path="/{user_id}",
    response_model=MessageResponse,
    summary="Update User",
    description="Update an existing user - Admin only",
    responses={
        200: {"description": "User updated successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "User not found"},
    },
)
async def update_existing_user(
    user_id: UUID,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(AuthMiddleware.get_current_admin),
) -> MessageResponse:
    """Update an existing user - Admin only"""

    user_service = UserService(db)
    updated_user = await user_service.update_user(user_id, user_update)
    return MessageResponse(
        message="User updated successfully", data=updated_user.model_dump()
    )


@router.delete(
    path="/{user_id}",
    response_model=MessageResponse,
    summary="Delete User",
    description="Delete an existing user - Admin only",
    responses={
        200: {"description": "User deleted successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "User not found"},
    },
)
async def delete_existing_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(AuthMiddleware.get_current_admin),
) -> MessageResponse:
    """Delete an existing user - Admin only"""

    user_service = UserService(db)
    success = await user_service.delete_user(user_id, current_user.id)
    return MessageResponse(message="User deleted successfully")


@router.post(
    path="/change-password/{user_id}",
    response_model=MessageResponse,
    summary="Change User Password",
    description="Change password for a user - Admin only",
    responses={
        200: {"description": "Password changed successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "User not found"},
    },
)
async def change_password(
    user_id: UUID,
    password_data: ChangePasswordRequest,
    current_user: Users = Depends(AuthMiddleware.get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Change password for a user - Admin only"""

    user_service = UserService(db=db)
    await user_service.change_password(
        user_id=user_id, new_password=password_data.new_password
    )
    return MessageResponse(message="Password changed successfully")
