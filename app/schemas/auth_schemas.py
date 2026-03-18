from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    role: Optional[str] = "USER"


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: Optional[str] = None


class TokenData(BaseModel):
    id: Optional[UUID] = None
    username: Optional[str] = None
    role: Optional[str] = None

class RefreshRequest(BaseModel):
    refresh_token: str