"""角色与权限 schema。"""

from __future__ import annotations

from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field


class PermissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    description: Optional[str] = None


class RoleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    description: Optional[str] = None
    permission_codes: List[str] = Field(default_factory=list)


class RoleUpdate(BaseModel):
    description: Optional[str] = None
    permission_codes: Optional[List[str]] = None


class RoleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: Optional[str]
    is_builtin: bool
    permissions: List[PermissionOut]
    member_count: int = 0
