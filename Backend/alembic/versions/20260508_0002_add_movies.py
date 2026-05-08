"""add movies table

Revision ID: 20260508_0002
Revises: 20260508_0001
Create Date: 2026-05-08 00:10:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260508_0002"
down_revision: Union[str, None] = "20260508_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "movies",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("original_title", sa.String(length=200), nullable=True),
        sa.Column("director", sa.String(length=120), nullable=True),
        sa.Column("cast", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("genres", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("rating", sa.String(length=20), nullable=True),
        sa.Column("synopsis", sa.Text(), nullable=False, server_default=""),
        sa.Column("cover_url", sa.String(length=500), nullable=True),
        sa.Column("video_url", sa.String(length=500), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("pinned", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "owner_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_movies_title", "movies", ["title"])
    op.create_index("ix_movies_pinned", "movies", ["pinned"])
    op.create_index("ix_movies_owner_id", "movies", ["owner_id"])
    op.create_index("ix_movies_pinned_updated", "movies", ["pinned", "updated_at"])


def downgrade() -> None:
    op.drop_index("ix_movies_pinned_updated", table_name="movies")
    op.drop_index("ix_movies_owner_id", table_name="movies")
    op.drop_index("ix_movies_pinned", table_name="movies")
    op.drop_index("ix_movies_title", table_name="movies")
    op.drop_table("movies")
