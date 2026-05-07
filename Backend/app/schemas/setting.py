"""站点设置 schema。"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class SettingItem(BaseModel):
    key: str
    value: Any
