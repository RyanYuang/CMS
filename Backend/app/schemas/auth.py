"""鉴权相关 schema。"""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=6, max_length=128)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int


class MeResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str | None
    avatar_url: str | None
    role: str | None
    permissions: List[str]
