"""用户 schema。"""

from __future__ import annotations

from datetime import datetime
from typing import List

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
    full_name: str | None = None
    role_id: int | None = None
    is_active: bool = True


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=6, max_length=128)
    full_name: str | None = None
    role_id: int | None = None
    is_active: bool | None = None
    avatar_url: str | None = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: str
    full_name: str | None
    is_active: bool
    avatar_url: str | None
    role: RoleBrief | None
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime


class UserList(BaseModel):
    items: List[UserOut]
    meta: PageMeta
