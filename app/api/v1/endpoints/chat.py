from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, WebSocket

from app.data_controllers.chat_history_data_controller import ChatHistoryDataController
from app.database.database import AsyncSessionLocal
from app.middleware.auth import AuthMiddleware
from app.models.chat_message import ChatSenderEnum
from app.schemas.chat_schemas import (
    ChatMessageCreateRequest,
    ChatMessageListResponse,
    ChatMessageResponse,
    ChatSessionCreateRequest,
    ChatSessionListResponse,
    ChatSessionResponse,
)
from app.services.chat_service import ChatService

router = APIRouter()


@router.websocket("/chat")
async def chat_websocket(
    websocket: WebSocket,
    user=Depends(AuthMiddleware.get_current_ws_user),
):
    if not user:
        return

    session_id = websocket.query_params.get("session_id")
    if not session_id:
        await websocket.close(code=4400)
        return

    try:
        parsed_session_id = UUID(session_id)
    except ValueError:
        await websocket.close(code=4400)
        return

    async with AsyncSessionLocal() as db:
        controller = ChatHistoryDataController(db)
        session = await controller.get_session_for_user(
            session_id=parsed_session_id,
            user_id=user.id,
        )
        if session is None:
            await websocket.close(code=4403)
            return

    service = ChatService()
    await service.handle_chat_websocket(
        websocket=websocket,
        user_id=user.id,
        session_id=parsed_session_id,
    )


@router.post("/session", response_model=ChatSessionResponse)
async def create_chat_session(
    req: ChatSessionCreateRequest,
    user=Depends(AuthMiddleware.get_current_user),
):
    async with AsyncSessionLocal() as db:
        controller = ChatHistoryDataController(db)
        session = await controller.create_session(user_id=user.id, title=req.title)
        return ChatSessionResponse(
            id=session.id, title=session.title, created_at=session.created_at, updated_at=session.updated_at
        )

@router.get("/sessions", response_model=ChatSessionListResponse)
async def list_chat_sessions(user=Depends(AuthMiddleware.get_current_user)):
    async with AsyncSessionLocal() as db:
        controller = ChatHistoryDataController(db)
        sessions = await controller.get_sessions(user_id=user.id)
        return ChatSessionListResponse(sessions=[
            ChatSessionResponse(
                id=s.id, title=s.title, created_at=s.created_at, updated_at=s.updated_at
            ) for s in sessions
        ])

@router.post("/message", response_model=ChatMessageResponse)
async def create_chat_message(
    req: ChatMessageCreateRequest,
    user=Depends(AuthMiddleware.get_current_user),
):
    async with AsyncSessionLocal() as db:
        controller = ChatHistoryDataController(db)
        session = await controller.get_session_for_user(
            session_id=req.session_id,
            user_id=user.id,
        )
        if session is None:
            raise HTTPException(status_code=404, detail="Chat session not found")

        msg = await controller.create_message(
            session_id=req.session_id,
            sender=ChatSenderEnum(req.sender.value),
            message=req.message,
        )
        return ChatMessageResponse(
            id=msg.id,
            session_id=msg.session_id,
            sender=msg.sender,
            message=msg.message,
            created_at=msg.created_at,
            updated_at=msg.updated_at,
        )

@router.get("/messages", response_model=ChatMessageListResponse)
async def list_chat_messages(
    session_id: UUID,
    user=Depends(AuthMiddleware.get_current_user),
):
    async with AsyncSessionLocal() as db:
        controller = ChatHistoryDataController(db)
        session = await controller.get_session_for_user(
            session_id=session_id,
            user_id=user.id,
        )
        if session is None:
            raise HTTPException(status_code=404, detail="Chat session not found")

        messages = await controller.get_messages(session_id=session_id)
        return ChatMessageListResponse(
            messages=[
                ChatMessageResponse(
                    id=m.id,
                    session_id=m.session_id,
                    sender=m.sender,
                    message=m.message,
                    created_at=m.created_at,
                    updated_at=m.updated_at,
                )
                for m in messages
            ]
        )
