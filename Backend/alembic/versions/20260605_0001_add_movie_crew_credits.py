"""add movies.crew_credits

Revision ID: 20260605_0001
Revises: 20260604_0001
Create Date: 2026-06-05

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from upgrade_compat import inspector

revision: str = "20260605_0001"
down_revision: Union[str, None] = "20260604_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if "movies" not in inspector().get_table_names():
        return
    cols = {c["name"] for c in inspector().get_columns("movies")}
    if "crew_credits" not in cols:
        op.add_column("movies", sa.Column("crew_credits", sa.JSON(), nullable=False, server_default="[]"))


def downgrade() -> None:
    if "movies" not in inspector().get_table_names():
        return
    cols = {c["name"] for c in inspector().get_columns("movies")}
    if "crew_credits" in cols:
        op.drop_column("movies", "crew_credits")
