"""add music tracks table

Revision ID: 20260508_0003
Revises: 20260508_0002
Create Date: 2026-05-08 00:20:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from upgrade_compat import create_indexes_if_missing, inspector


revision: str = "20260508_0003"
down_revision: Union[str, None] = "20260508_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if "music_tracks" not in inspector().get_table_names():
        op.create_table(
            "music_tracks",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("title", sa.String(length=200), nullable=False),
            sa.Column("artist", sa.String(length=200), nullable=True),
            sa.Column("album", sa.String(length=200), nullable=True),
            sa.Column("genre", sa.String(length=80), nullable=True),
            sa.Column("year", sa.Integer(), nullable=True),
            sa.Column("duration_seconds", sa.Integer(), nullable=True),
            sa.Column("cover_url", sa.String(length=500), nullable=True),
            sa.Column("audio_url", sa.String(length=500), nullable=True),
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
    create_indexes_if_missing(
        "music_tracks",
        [
            ("ix_music_tracks_title", ["title"]),
            ("ix_music_tracks_pinned", ["pinned"]),
            ("ix_music_tracks_owner_id", ["owner_id"]),
            ("ix_music_tracks_pinned_updated", ["pinned", "updated_at"]),
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_music_tracks_pinned_updated", table_name="music_tracks")
    op.drop_index("ix_music_tracks_owner_id", table_name="music_tracks")
    op.drop_index("ix_music_tracks_pinned", table_name="music_tracks")
    op.drop_index("ix_music_tracks_title", table_name="music_tracks")
    op.drop_table("music_tracks")
