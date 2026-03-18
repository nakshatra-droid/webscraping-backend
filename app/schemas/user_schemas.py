import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.constants.constants import Roles


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    role: str = Field(default=Roles.USER)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip().lower()  # strip + lowercase

        if " " in v:
            raise ValueError("Username must not contain spaces.")

        if not re.fullmatch(r"[a-z0-9]+", v):
            raise ValueError("Username can contain only lowercase letters and numbers.")

        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in {Roles.USER, Roles.ADMIN}:
            raise ValueError("Role must be either USER or ADMIN.")
        return v


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(default=None, min_length=3, max_length=50)
    role: Optional[str] = Field(default=Roles.USER)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v

        v = v.strip().lower()

        if " " in v:
            raise ValueError("Username must not contain spaces.")

        if not re.fullmatch(r"[a-z0-9]+", v):
            raise ValueError("Username can contain only lowercase letters and numbers.")

        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v

        if v not in {Roles.USER, Roles.ADMIN}:
            raise ValueError("Role must be either USER or ADMIN.")

        return v


class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChangePasswordRequest(BaseModel):
    new_password: str = Field(min_length=6)
