from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage, ChatSenderEnum
from uuid import UUID
from typing import List, Optional


class ChatHistoryDataController:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(
        self, user_id: UUID, title: Optional[str] = None
    ) -> ChatSession:
        session = ChatSession(user_id=user_id, title=title)
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_sessions(self, user_id: UUID) -> List[ChatSession]:
        result = await self.db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == user_id, ChatSession.deleted_at.is_(None))
            .order_by(ChatSession.updated_at.desc())
        )
        return result.scalars().all()

    async def get_session_for_user(
        self, session_id: UUID, user_id: UUID
    ) -> Optional[ChatSession]:
        result = await self.db.execute(
            select(ChatSession).where(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id,
                ChatSession.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def create_message(
        self, session_id: UUID, sender: ChatSenderEnum, message: dict
    ) -> ChatMessage:
        msg = ChatMessage(session_id=session_id, sender=sender, message=message)
        self.db.add(msg)
        await self.db.commit()
        await self.db.refresh(msg)
        return msg

    async def get_messages(self, session_id: UUID) -> List[ChatMessage]:
        result = await self.db.execute(
            select(ChatMessage)
            .where(
                ChatMessage.session_id == session_id,
                ChatMessage.deleted_at.is_(None),
            )
            .order_by(ChatMessage.created_at)
        )
        return result.scalars().all()
