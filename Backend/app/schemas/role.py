"""角色与权限 schema。"""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, ConfigDict, Field


class PermissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    description: str | None = None


class RoleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    description: str | None = None
    permission_codes: List[str] = Field(default_factory=list)


class RoleUpdate(BaseModel):
    description: str | None = None
    permission_codes: List[str] | None = None


class RoleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str | None
    is_builtin: bool
    permissions: List[PermissionOut]
    member_count: int = 0
