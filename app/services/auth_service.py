from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions import UnauthorizedException
from app.data_controllers.user_data_controller import UserDataController
from app.schemas.auth_schemas import UserLogin, Token
from app.utils.jwt_utils import JWTUtils
from app.data_controllers.auth_data_controller import AuthDataController
from jose import JWTError, jwt
from app.config.config import Config
from uuid import UUID


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.controller = UserDataController(db)
        self.controller_auth = AuthDataController(db)

    async def login(self, user_data: UserLogin) -> dict:
        """Authenticate a user and return an access token"""

        user = await self.controller.get_user_by_username(username=user_data.username)

        if not user:
            raise UnauthorizedException("User does not exist. Enter a valid username")

        if not JWTUtils.verify_password(
            plain_password=user_data.password, hashed_password=user.password
        ):
            raise UnauthorizedException("Invalid password. Please try again")

        access_token = JWTUtils.create_access_token(
            data={"sub": user.username, "role": user.role, "user_id": str(user.id)}
        )
        refresh_token = JWTUtils.create_refresh_token(
            data={"sub": user.username, "role": user.role, "user_id": str(user.id)}
        )
        hashed_token = JWTUtils.hash_token(refresh_token)
        refresh_success = await self.controller_auth.store_refresh_token(
            user.id, hashed_token
        )
        if not refresh_success:
            raise UnauthorizedException(
                "Failed to store refresh token. Please try again"
            )
        token_data = Token(access_token=access_token, refresh_token=refresh_token, role=str(user.role))
        return token_data.model_dump()

    async def refresh_token(self, refresh_token: str) -> dict:
        """Refresh access token using a valid refresh token"""

        try:
            payload = jwt.decode(refresh_token, Config.SECRET_KEY, algorithms=["HS256"])
        except JWTError:
            raise UnauthorizedException("Invalid refresh token. Please try again")

        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid token type")

        user_id = UUID(payload.get("user_id"))

        db_refresh_token = await self.controller_auth.get_refresh_token(user_id)

        if not db_refresh_token:
            raise UnauthorizedException(
                "Refresh token not found. Enter a valid refresh token"
            )

        if db_refresh_token.is_refresh_revoked:
            raise UnauthorizedException(
                "Refresh token has been revoked. Please login again"
            )

        if not JWTUtils.verify_refresh_token(
            refresh_token, db_refresh_token.refresh_token
        ):
            raise UnauthorizedException("Invalid refresh token")

        new_access_token = JWTUtils.create_access_token(
            data={
                "sub": payload.get("sub"),
                "role": payload.get("role"),
                "user_id": str(payload.get("user_id")),
            }
        )
        new_refresh_token = JWTUtils.create_refresh_token(
            data={
                "sub": payload.get("sub"),
                "role": payload.get("role"),
                "user_id": str(payload.get("user_id")),
            }
        )
        hashed_token = JWTUtils.hash_token(new_refresh_token)
        refresh_success = await self.controller_auth.store_refresh_token(
            user_id, hashed_token
        )
        if not refresh_success:
            raise UnauthorizedException(
                "Failed to store refresh token. Please try again"
            )
        token_data = Token(
            access_token=new_access_token, refresh_token=new_refresh_token, role=payload.get("role")
        )
        return token_data.model_dump()

    async def logout(self, user_id: UUID) -> bool:
        """Logout user by revoking refresh token"""

        success = await self.controller_auth.logout(user_id=user_id)
        if not success:
            raise UnauthorizedException("Failed to logout. Please try again")
        return True
