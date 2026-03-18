from fastapi import Depends, Request, WebSocket
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.users import Users
from app.constants.constants import Roles

security = HTTPBearer()


class AuthMiddleware:
    @staticmethod
    async def get_current_ws_user(websocket: WebSocket):
        user = websocket.scope.get("user")
        if not user:
            await websocket.close(code=4401)
            return
        return user

    @staticmethod
    async def get_current_user(
        request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        user = request.scope.get("user")
        if not user:
            return JSONResponse(
                status_code=401,
                content={
                    "success": False,
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": "Missing or invalid Authorization header",
                        "details": {},
                    },
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    @staticmethod
    async def get_current_admin(current_user: Users = Depends(get_current_user)):
        if current_user.role != Roles.ADMIN:
            from app.exceptions import ForbiddenException

            raise ForbiddenException("No admin privileges")
        return current_user
