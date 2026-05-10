"""slug 生成与去重工具。"""

from __future__ import annotations

import secrets
from typing import Optional

from slugify import slugify


def make_slug(text: str, *, fallback: Optional[str] = None) -> str:
    base = slugify(text or "", lowercase=True, max_length=120)
    if not base:
        base = fallback or f"item-{secrets.token_hex(3)}"
    return base


def with_suffix(slug: str) -> str:
    return f"{slug}-{secrets.token_hex(3)}"
