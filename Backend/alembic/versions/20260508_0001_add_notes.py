"""add notes table

Revision ID: 20260508_0001
Revises:
Create Date: 2026-05-08 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from upgrade_compat import create_indexes_if_missing, inspector


revision: str = "20260508_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if "notes" not in inspector().get_table_names():
        op.create_table(
            "notes",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("title", sa.String(length=200), nullable=False),
            sa.Column("content", sa.Text(), nullable=False, server_default=""),
            sa.Column("category", sa.String(length=80), nullable=True),
            sa.Column("pinned", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("tags", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
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
    create_indexes_if_missing(
        "notes",
        [
            ("ix_notes_title", ["title"]),
            ("ix_notes_category", ["category"]),
            ("ix_notes_pinned", ["pinned"]),
            ("ix_notes_owner_id", ["owner_id"]),
            ("ix_notes_pinned_updated", ["pinned", "updated_at"]),
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_notes_pinned_updated", table_name="notes")
    op.drop_index("ix_notes_owner_id", table_name="notes")
    op.drop_index("ix_notes_pinned", table_name="notes")
    op.drop_index("ix_notes_category", table_name="notes")
    op.drop_index("ix_notes_title", table_name="notes")
    op.drop_table("notes")
