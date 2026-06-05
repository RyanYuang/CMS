"""add movies.production_sheet_url

Revision ID: 20260604_0001
Revises: 20260518_0001
Create Date: 2026-06-04

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from upgrade_compat import inspector

revision: str = "20260604_0001"
down_revision: Union[str, None] = "20260518_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if "movies" not in inspector().get_table_names():
        return
    cols = {c["name"] for c in inspector().get_columns("movies")}
    if "production_sheet_url" not in cols:
        op.add_column("movies", sa.Column("production_sheet_url", sa.String(length=500), nullable=True))


def downgrade() -> None:
    if "movies" not in inspector().get_table_names():
        return
    cols = {c["name"] for c in inspector().get_columns("movies")}
    if "production_sheet_url" in cols:
        op.drop_column("movies", "production_sheet_url")
