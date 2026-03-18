from uuid import UUID
from datetime import datetime
from enum import Enum
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class ChatSenderEnum(str, Enum):
    USER = "USER"
    BOT = "BOT"


class ChatSessionCreateRequest(BaseModel):
    title: Optional[str] = None


class ChatSessionResponse(BaseModel):
    id: UUID
    title: Optional[str]
    created_at: datetime
    updated_at: datetime


class ChatMessageCreateRequest(BaseModel):
    session_id: UUID
    sender: ChatSenderEnum
    message: dict


class ChatMessageResponse(BaseModel):
    id: UUID
    session_id: UUID
    sender: ChatSenderEnum
    message: dict
    created_at: datetime
    updated_at: datetime


class ChatSessionListResponse(BaseModel):
    sessions: List[ChatSessionResponse]


class ChatMessageListResponse(BaseModel):
    messages: List[ChatMessageResponse]
