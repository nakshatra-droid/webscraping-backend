from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from sqlalchemy.exc import IntegrityError
from app.exceptions import ConflictException
from app.models.users import Users
from app.schemas.user_schemas import UserCreate, UserUpdate
from typing import Optional, Dict, Any
from uuid import UUID
import math


class UserDataController:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: UserCreate, hashed_password: str) -> Users:
        """Create a new user - Admin only"""
        try:
            user = Users(
                username=user_data.username,
                password=hashed_password,
                role=user_data.role,
            )
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except IntegrityError:
            await self.db.rollback()
            raise ConflictException(
                "Username already exists. Please choose a different username."
            )
        except Exception:
            await self.db.rollback()
            raise

    async def get_user_by_id(self, user_id: UUID) -> Optional[Users]:
        """Get a user by their ID - Admin only"""

        result = await self.db.execute(
            select(Users).where(Users.id == user_id, Users.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> Optional[Users]:
        """Get a user by their username - Admin only"""

        result = await self.db.execute(
            select(Users).where(
                Users.username == username,
                Users.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_all_users(self, page: int, size: int) -> Dict[str, Any]:
        """Get all users - Admin only"""

        skip = (page - 1) * size

        # Get total count
        total_result = await self.db.execute(
            select(func.count(Users.id)).where(Users.deleted_at.is_(None))
        )
        total = total_result.scalar()

        # Get paginated data
        result = await self.db.execute(
            select(Users)
            .where(Users.deleted_at.is_(None))
            .order_by(Users.created_at.desc())
            .offset(skip)
            .limit(size)
        )
        data = result.scalars().all()

        pages = math.ceil(total / size) if total > 0 else 0

        return {
            "total": total,
            "page": page,
            "size": size,
            "pages": pages,
            "data": data,
        }

    async def update_user(
        self, user_id: UUID, user_data: UserUpdate
    ) -> Optional[Users]:
        """Update a user - Admin only"""

        try:
            update_data = user_data.model_dump(exclude_unset=True)

            result = await self.db.execute(
                update(Users)
                .where(
                    Users.id == user_id,
                    Users.deleted_at.is_(None),
                )
                .values(**update_data)
                .returning(Users)
            )

            user = result.scalar_one_or_none()

            if not user:
                await self.db.rollback()
                return None
            else:
                await self.db.commit()
                return user
        except Exception:
            await self.db.rollback()
            raise

    async def delete_user(self, user_id: UUID) -> bool:
        """Delete a user - Admin only"""

        try:
            result = await self.db.execute(
                update(Users)
                .where(
                    Users.id == user_id,
                    Users.deleted_at.is_(None),
                )
                .values(deleted_at=func.now())
                .returning(Users.id)
            )
            user = result.scalar_one_or_none()

            if not user:
                await self.db.rollback()
                return False
            else:
                await self.db.commit()
                return True
        except Exception:
            await self.db.rollback()
            raise

    async def update_user_password(self, user_id: UUID, hashed_password: str) -> bool:
        """Update a user's password - Admin only"""
        try:
            result = await self.db.execute(
                update(Users)
                .where(
                    Users.id == user_id,
                    Users.deleted_at.is_(None),
                )
                .values(password=hashed_password)
                .returning(Users.id)
            )
            success = result.scalar_one_or_none()

            if not success:
                await self.db.rollback()
                return False
            else:
                await self.db.commit()
                return True
        except Exception:
            await self.db.rollback()
            raise
