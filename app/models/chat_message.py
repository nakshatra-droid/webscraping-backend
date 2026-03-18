from datetime import datetime
from sqlalchemy import Uuid, ForeignKey, DateTime, func, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base
import enum


class ChatSenderEnum(enum.Enum):
    USER = "USER"
    BOT = "BOT"


class ChatMessage(Base):
    __tablename__ = "chat_message"
    id: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=func.gen_random_uuid(),
        nullable=False,
        index=True,
    )
    session_id: Mapped[Uuid] = mapped_column(
        ForeignKey("chat_session.id"), nullable=False
    )
    sender: Mapped[ChatSenderEnum] = mapped_column(Enum(ChatSenderEnum), nullable=False)
    message: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    session = relationship("ChatSession", back_populates="messages")
