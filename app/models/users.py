from datetime import datetime
from sqlalchemy import String, DateTime, Text, Uuid, Boolean
from sqlalchemy.sql import func
from app.database.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from app.models.enums import user_role_enum


class Users(Base):
    __tablename__ = "users"

    id: Mapped[Uuid] = mapped_column(
        Uuid,
        primary_key=True,
        index=True,
        default=func.gen_random_uuid(),
        nullable=False,
    )
    username: Mapped[str] = mapped_column(
        String, unique=True, nullable=False, index=True
    )
    password: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(user_role_enum, nullable=False, default="USER")
    refresh_token: Mapped[str] = mapped_column(Text, nullable=True)
    is_refresh_revoked: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
