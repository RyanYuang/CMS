"""与「仅 create_all、无 alembic_version」的旧库兼容：迁移在对象已存在时跳过。"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


def inspector():
    return sa.inspect(op.get_bind())


def create_indexes_if_missing(table: str, specs: list[tuple[str, list[str]]]) -> None:
    if table not in inspector().get_table_names():
        return
    existing = {ix["name"] for ix in inspector().get_indexes(table)}
    for name, columns in specs:
        if name not in existing:
            op.create_index(name, table, columns)
