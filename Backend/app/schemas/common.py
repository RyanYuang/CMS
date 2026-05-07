"""通用响应模型。"""

from __future__ import annotations

from typing import Generic, List, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T")


class OkResponse(BaseModel):
    ok: bool = True
    message: str = "success"


class PageMeta(BaseModel):
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=200)
    total: int = Field(ge=0)
    total_pages: int = Field(ge=0)


class Page(BaseModel, Generic[T]):
    items: List[T]
    meta: PageMeta
