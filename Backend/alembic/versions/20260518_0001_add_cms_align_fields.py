"""add work_category, music photos/story, note written_at

Revision ID: 20260518_0001
Revises: 20260508_0004
Create Date: 2026-05-18

"""
from __future__ import annotations

import json
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from upgrade_compat import inspector


revision: str = "20260518_0001"
down_revision: Union[str, None] = "20260508_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _parse_json_list(raw) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(item) for item in raw if item is not None]
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return [str(item) for item in parsed if item is not None]
        except json.JSONDecodeError:
            return []
    return []


def _detect_work_category(tags: list[str], genres: list[str]) -> str:
    values = [*(tags or []), *(genres or [])]
    normalized = [str(item).strip().lower() for item in values]
    if any(item in {"short", "short-film", "短片"} for item in normalized):
        return "short"
    if any(item in {"media", "self-media", "自媒体"} for item in normalized):
        return "media"
    return "feature"


def _backfill_movie_work_category(connection) -> None:
    if "movies" not in inspector().get_table_names():
        return
    cols = {c["name"] for c in inspector().get_columns("movies")}
    if "work_category" not in cols:
        return
    rows = connection.execute(sa.text("SELECT id, tags, genres FROM movies")).fetchall()
    for row in rows:
        tags = _parse_json_list(row.tags)
        genres = _parse_json_list(row.genres)
        category = _detect_work_category(tags, genres)
        connection.execute(
            sa.text("UPDATE movies SET work_category = :cat WHERE id = :id"),
            {"cat": category, "id": row.id},
        )


def upgrade() -> None:
    insp = inspector()
    tables = set(insp.get_table_names())

    if "movies" in tables:
        movie_cols = {c["name"] for c in insp.get_columns("movies")}
        if "work_category" not in movie_cols:
            op.add_column(
                "movies",
                sa.Column(
                    "work_category",
                    sa.String(length=20),
                    nullable=False,
                    server_default="feature",
                ),
            )
            op.create_index("ix_movies_work_category", "movies", ["work_category"], unique=False)

    if "music_tracks" in tables:
        music_cols = {c["name"] for c in insp.get_columns("music_tracks")}
        if "photos" not in music_cols:
            op.add_column(
                "music_tracks",
                sa.Column("photos", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
            )
        if "story" not in music_cols:
            op.add_column(
                "music_tracks",
                sa.Column("story", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
            )

    if "notes" in tables:
        note_cols = {c["name"] for c in insp.get_columns("notes")}
        if "written_at" not in note_cols:
            op.add_column("notes", sa.Column("written_at", sa.DateTime(timezone=True), nullable=True))
            op.create_index("ix_notes_written_at", "notes", ["written_at"], unique=False)

    connection = op.get_bind()
    _backfill_movie_work_category(connection)


def downgrade() -> None:
    if "movies" in inspector().get_table_names():
        movie_cols = {c["name"] for c in inspector().get_columns("movies")}
        if "work_category" in movie_cols:
            op.drop_index("ix_movies_work_category", table_name="movies")
            op.drop_column("movies", "work_category")

    if "music_tracks" in inspector().get_table_names():
        music_cols = {c["name"] for c in inspector().get_columns("music_tracks")}
        if "photos" in music_cols:
            op.drop_column("music_tracks", "photos")
        if "story" in music_cols:
            op.drop_column("music_tracks", "story")

    if "notes" in inspector().get_table_names():
        note_cols = {c["name"] for c in inspector().get_columns("notes")}
        if "written_at" in note_cols:
            op.drop_index("ix_notes_written_at", table_name="notes")
            op.drop_column("notes", "written_at")
