"""分页工具。"""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil

from fastapi import Query

from app.schemas.common import PageMeta


@dataclass
class PageParams:
    page: int
    page_size: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


def page_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
) -> PageParams:
    return PageParams(page=page, page_size=page_size)


def build_page_meta(params: PageParams, total: int) -> PageMeta:
    total_pages = ceil(total / params.page_size) if params.page_size else 0
    return PageMeta(
        page=params.page,
        page_size=params.page_size,
        total=total,
        total_pages=total_pages,
    )
