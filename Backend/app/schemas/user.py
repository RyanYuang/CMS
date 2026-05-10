"""用户 schema。"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.common import PageMeta


class RoleBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    full_name: Optional[str] = None
    role_id: Optional[int] = None
    is_active: bool = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(default=None, min_length=6, max_length=128)
    full_name: Optional[str] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None
    avatar_url: Optional[str] = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    avatar_url: Optional[str]
    role: Optional[RoleBrief]
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class UserList(BaseModel):
    items: List[UserOut]
    meta: PageMeta
