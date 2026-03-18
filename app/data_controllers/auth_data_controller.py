from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select
from app.models.users import Users
from uuid import UUID


class AuthDataController:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def store_refresh_token(self, user_id: UUID, refresh_token: str) -> bool:
        """Store the refresh token for a user"""

        try:
            result = await self.db.execute(
                update(Users)
                .where(
                    Users.id == user_id,
                    Users.deleted_at.is_(None),
                )
                .values(refresh_token=refresh_token, is_refresh_revoked=False)
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

    async def get_refresh_token(self, user_id: UUID) -> str:
        """Get refresh token for a user"""

        try:
            result = await self.db.execute(select(Users).where(Users.id == user_id))
            refresh_token_data = result.scalar_one_or_none()
            if not refresh_token_data:
                return None
            else:
                return refresh_token_data
        except Exception:
            raise

    async def logout(self, user_id: UUID) -> bool:
        """Logout user by revoking refresh token"""

        try:
            result = await self.db.execute(
                update(Users)
                .where(
                    Users.id == user_id,
                    Users.deleted_at.is_(None),
                )
                .values(is_refresh_revoked=True)
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
