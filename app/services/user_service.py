from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions import NotFoundException, ValidationException
from app.data_controllers.user_data_controller import UserDataController
from app.schemas.user_schemas import UserCreate, UserUpdate, UserResponse
from app.utils.jwt_utils import JWTUtils
from typing import Dict, Any
from uuid import UUID


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.controller = UserDataController(db)

    async def get_all_users(self, page: int = 1, size: int = 10) -> Dict[str, Any]:
        """Get all users in the system - Admin only"""

        result = await self.controller.get_all_users(page, size)
        result["data"] = [UserResponse.model_validate(user) for user in result["data"]]
        return result

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user - Admin only"""

        hashed_password = JWTUtils.get_password_hash(user_data.password)
        user = await self.controller.create_user(user_data, hashed_password)
        return UserResponse.model_validate(user)

    async def get_user_by_id(self, user_id: UUID) -> UserResponse:
        """Get a specific user by their ID - Admin only"""

        user = await self.controller.get_user_by_id(user_id)

        if not user:
            raise NotFoundException("User not found")
        return UserResponse.model_validate(user)

    async def update_user(self, user_id: UUID, user_update: UserUpdate) -> UserResponse:
        """Update a specific user by their ID - Admin only"""

        update_data = user_update.model_dump(exclude_unset=True)
        if not update_data:
            raise ValidationException("No update data provided")

        user = await self.controller.update_user(user_id, user_update)

        if not user:
            raise NotFoundException("User not found")
        return UserResponse.model_validate(user)

    async def delete_user(self, user_id: UUID, current_user_id: UUID) -> bool:
        """Delete a specific user by their ID - Admin only"""

        if user_id == current_user_id:
            raise ValidationException("Users cannot delete themselves")

        success = await self.controller.delete_user(user_id)
        if not success:
            raise NotFoundException("User not found")
        else:
            return True

    async def change_password(self, user_id: UUID, new_password: str) -> bool:
        """Change password for a user - Admin only"""

        hashed_password = JWTUtils.get_password_hash(new_password)
        success = await self.controller.update_user_password(user_id, hashed_password)
        if not success:
            raise NotFoundException("User not found")
        else:
            return True
