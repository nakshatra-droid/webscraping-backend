from starlette.types import ASGIApp, Scope, Receive, Send
from jose import JWTError, jwt, ExpiredSignatureError
from app.constants.constants import PublicRoutes
from app.config.config import Config
from app.data_controllers.user_data_controller import UserDataController
from app.database.database import AsyncSessionLocal
from uuid import UUID
import json


class AuthASGIMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        path = scope.get("path", "")
        if path in PublicRoutes.ROUTES or path.startswith("/static/"):
            await self.app(scope, receive, send)
            return

        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            auth_header = headers.get(b"authorization")

            if not auth_header or not auth_header.startswith(b"Bearer "):
                await self._unauthorized_http(
                    send, "Missing or invalid Authorization header"
                )
                return
            token = auth_header.split(b" ")[1].decode()

            try:
                payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])

                if payload.get("type") != "access":
                    await self._unauthorized_http(send, "Invalid token type")
                    return

                username = payload.get("sub")
                id = UUID(payload.get("user_id"))
                role = payload.get("role")

                if username is None:
                    await self._unauthorized_http(send, "Invalid credentials")
                    return

                async with AsyncSessionLocal() as db:
                    user_controller = UserDataController(db)
                    user = await user_controller.get_user_by_id(id)

                if user is None:
                    await self._unauthorized_http(send, "User does not exist")
                    return
                scope["user"] = user

            except ExpiredSignatureError:
                await self._unauthorized_http(send, "Token has expired")
                return
            except (JWTError, ValueError):
                await self._unauthorized_http(send, "Invalid credentials")
                return
            await self.app(scope, receive, send)

        elif scope["type"] == "websocket":
            token = None
            headers = dict(scope.get("headers", []))
            if b"authorization" in headers:
                auth_header = headers[b"authorization"].decode()
                if auth_header.startswith("Bearer "):
                    token = auth_header.split(" ")[1]

            if not token:
                query_string = scope.get("query_string", b"").decode()
                for part in query_string.split("&"):
                    if part.startswith("token="):
                        token = part.split("=", 1)[1]
                        break

            if not token:
                await self._unauthorized_ws(send)
                return

            try:
                payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])

                if payload.get("type") != "access":
                    await self._unauthorized_ws(send)
                    return

                username = payload.get("sub")
                id = UUID(payload.get("user_id"))
                role = payload.get("role")

                if username is None:
                    await self._unauthorized_ws(send)
                    return

                async with AsyncSessionLocal() as db:
                    user_controller = UserDataController(db)
                    user = await user_controller.get_user_by_id(id)

                if user is None:
                    await self._unauthorized_ws(send)
                    return
                scope["user"] = user

            except ExpiredSignatureError:
                await self._unauthorized_ws(send)
                return
            except (JWTError, ValueError):
                await self._unauthorized_ws(send)
                return
            await self.app(scope, receive, send)

        else:
            await self.app(scope, receive, send)

    async def _unauthorized_http(self, send: Send, message: str):
        await send(
            {
                "type": "http.response.start",
                "status": 401,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"www-authenticate", b"Bearer"),
                ],
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": json.dumps(
                    {
                        "success": False,
                        "error": {
                            "code": "UNAUTHORIZED",
                            "message": message,
                            "details": {},
                        },
                    }
                ).encode(),
            }
        )

    async def _unauthorized_ws(self, send: Send):
        await send({"type": "websocket.close", "code": 4401})
