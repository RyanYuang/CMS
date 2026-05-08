"""Public API：供 Leowongwebsite 等前台站点匿名访问（RYA-10）。"""


from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.exceptions import NotFound
from app.models import (
    Article,
    ArticleStatus,
    Asset,
    AssetKind,
    LinkItem,
    LinkStatus,
    Movie,
    MusicTrack,
    Note,
    SiteSetting,
)
from app.schemas import ArticleDetail, ArticleListItem, AssetOut, LinkOut
from app.schemas.common import Page
from app.services import article as article_service
from app.utils.pagination import PageParams, build_page_meta, page_params


router = APIRouter(prefix="/public", tags=["public"])


class PublicNoteOut(BaseModel):
    id: int
    title: str
    content: str
    category: str | None
    pinned: bool
    tags: list[str]
    created_at: datetime
    updated_at: datetime


class PublicMovieOut(BaseModel):
    id: int
    title: str
    original_title: str | None
    year: int | None
    synopsis: str
    cover_url: str | None
    video_url: str | None
    stills: list[str]
    genres: list[str]
    tags: list[str]
    pinned: bool
    updated_at: datetime


class PublicMusicOut(BaseModel):
    id: int
    title: str
    artist: str | None
    album: str | None
    year: int | None
    cover_url: str | None
    audio_url: str | None
    tags: list[str]
    pinned: bool
    updated_at: datetime


def _serialize_note_tags(value) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(tag) for tag in value if tag is not None]
    return []


def _serialize_string_list(value) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    return []


@router.get("/articles", response_model=Page[ArticleListItem])
async def public_articles(
    keyword: str | None = Query(None, max_length=120),
    category_id: int | None = Query(None),
    tag_id: int | None = Query(None),
    pp: PageParams = Depends(page_params),
    session: AsyncSession = Depends(get_session),
) -> Page[ArticleListItem]:
    rows, total = await article_service.list_articles(
        session,
        keyword=keyword,
        status=ArticleStatus.published,
        category_id=category_id,
        tag_id=tag_id,
        author_id=None,
        date_from=None,
        date_to=None,
        offset=pp.offset,
        limit=pp.page_size,
        only_published=True,
    )
    return Page[ArticleListItem](
        items=[ArticleListItem.model_validate(a) for a in rows],
        meta=build_page_meta(pp, total),
    )


@router.get("/articles/{slug}", response_model=ArticleDetail)
async def public_article_detail(
    slug: str,
    session: AsyncSession = Depends(get_session),
) -> ArticleDetail:
    res = await session.execute(
        select(Article).where(Article.slug == slug, Article.status == ArticleStatus.published)
    )
    article = res.scalar_one_or_none()
    if not article:
        raise NotFound("文章不存在或未发布")
    article.view_count += 1
    await session.flush()
    fresh = (
        await session.execute(select(Article).where(Article.id == article.id))
    ).scalar_one()
    return ArticleDetail.model_validate(fresh)


@router.get("/links", response_model=list[LinkOut])
async def public_links(session: AsyncSession = Depends(get_session)) -> list[LinkOut]:
    res = await session.execute(
        select(LinkItem).where(LinkItem.status == LinkStatus.online).order_by(LinkItem.sort_order)
    )
    return [LinkOut.model_validate(i) for i in res.scalars().all()]


@router.get("/site")
async def public_site(session: AsyncSession = Depends(get_session)) -> dict:
    res = await session.execute(select(SiteSetting))
    return {s.key: s.value for s in res.scalars().all()}


@router.get("/assets", response_model=list[AssetOut])
async def public_assets(
    kind: AssetKind | None = Query(None),
    limit: int = Query(200, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
) -> list[AssetOut]:
    stmt = select(Asset)
    if kind is not None:
        stmt = stmt.where(Asset.kind == kind)

    rows = (await session.execute(stmt.order_by(Asset.id.desc()).limit(limit))).scalars().all()
    return [AssetOut.model_validate(i) for i in rows]


@router.get("/movies", response_model=list[PublicMovieOut])
async def public_movies(
    limit: int = Query(200, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
) -> list[PublicMovieOut]:
    rows = (
        await session.execute(
            select(Movie).order_by(Movie.pinned.desc(), Movie.updated_at.desc(), Movie.id.desc()).limit(limit)
        )
    ).scalars().all()
    return [
        PublicMovieOut(
            id=movie.id,
            title=movie.title,
            original_title=movie.original_title,
            year=movie.year,
            synopsis=movie.synopsis or "",
            cover_url=movie.cover_url,
            video_url=movie.video_url,
            stills=_serialize_string_list(movie.stills),
            genres=_serialize_string_list(movie.genres),
            tags=_serialize_string_list(movie.tags),
            pinned=bool(movie.pinned),
            updated_at=movie.updated_at,
        )
        for movie in rows
    ]


@router.get("/music", response_model=list[PublicMusicOut])
async def public_music(
    limit: int = Query(200, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
) -> list[PublicMusicOut]:
    rows = (
        await session.execute(
            select(MusicTrack)
            .order_by(MusicTrack.pinned.desc(), MusicTrack.updated_at.desc(), MusicTrack.id.desc())
            .limit(limit)
        )
    ).scalars().all()
    return [
        PublicMusicOut(
            id=track.id,
            title=track.title,
            artist=track.artist,
            album=track.album,
            year=track.year,
            cover_url=track.cover_url,
            audio_url=track.audio_url,
            tags=_serialize_string_list(track.tags),
            pinned=bool(track.pinned),
            updated_at=track.updated_at,
        )
        for track in rows
    ]


@router.get("/notes", response_model=Page[PublicNoteOut])
async def public_notes(
    pp: PageParams = Depends(page_params),
    session: AsyncSession = Depends(get_session),
) -> Page[PublicNoteOut]:
    stmt = (
        select(Note)
        .order_by(Note.pinned.desc(), Note.updated_at.desc(), Note.id.desc())
        .offset(pp.offset)
        .limit(pp.page_size)
    )
    count_stmt = select(func.count()).select_from(Note)

    rows = (await session.execute(stmt)).scalars().all()
    total = (await session.execute(count_stmt)).scalar_one()

    return Page[PublicNoteOut](
        items=[
            PublicNoteOut(
                id=note.id,
                title=note.title,
                content=note.content or "",
                category=note.category,
                pinned=bool(note.pinned),
                tags=_serialize_note_tags(note.tags),
                created_at=note.created_at,
                updated_at=note.updated_at,
            )
            for note in rows
        ],
        meta=build_page_meta(pp, total),
    )
