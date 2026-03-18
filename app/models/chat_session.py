from datetime import datetime
from sqlalchemy import Uuid, ForeignKey, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base


class ChatSession(Base):
    __tablename__ = "chat_session"
    id: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=func.gen_random_uuid(),
        nullable=False,
        index=True,
    )
    user_id: Mapped[Uuid] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    messages = relationship(
        "ChatMessage", back_populates="session", cascade="all, delete-orphan"
    )
