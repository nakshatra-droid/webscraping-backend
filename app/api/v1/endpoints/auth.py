from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.schemas.auth_schemas import UserLogin
from app.schemas.common_schemas import MessageResponse
from app.services.auth_service import AuthService
from app.middleware.auth import AuthMiddleware
from app.models.users import Users

router = APIRouter()


@router.post(
    path="/login",
    response_model=MessageResponse,
    summary="User Login",
    description="Authenticate user and return access token",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid credentials"},
    },
)
async def login(
    user_data: UserLogin, db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """Login user and return access token"""
    auth_service = AuthService(db=db)
    token_data = await auth_service.login(user_data=user_data)
    return MessageResponse(message="Login successful", data=token_data)


@router.post(
    path="/refresh",
    response_model=MessageResponse,
    summary="Refresh Access Token",
    description="Refresh access token using a valid refresh token",
    responses={
        200: {"description": "Token refreshed successfully"},
        401: {"description": "Invalid refresh token"},
    },
)
async def refresh_token(
    refresh_token: str, db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """Refresh access token using a valid refresh token"""
    auth_service = AuthService(db=db)
    new_token_data = await auth_service.refresh_token(refresh_token=refresh_token)
    return MessageResponse(message="Token refreshed successfully", data=new_token_data)


@router.post(
    path="/logout",
    response_model=MessageResponse,
    summary="Logout User",
    description="Revoke refresh token for a user",
    responses={200: {"description": "Logout successful"}},
)
async def logout(db: AsyncSession = Depends(get_db),current_user: Users = Depends(AuthMiddleware.get_current_user)) -> MessageResponse:
    """Logout user by revoking refresh token"""
    auth_service = AuthService(db=db)
    await auth_service.logout(user_id=current_user.id)
    return MessageResponse(message="Logout successful")
