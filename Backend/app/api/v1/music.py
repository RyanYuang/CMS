"""音乐接口：list/get/create/update/delete/togglePin/count。"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import current_user, require_permissions
from app.exceptions import NotFound
from app.models import AuditAction, MusicTrack, User
from app.permissions import Perm
from app.schemas import MusicTrackCount, MusicTrackCreate, MusicTrackOut, MusicTrackUpdate, OkResponse
from app.schemas.common import Page
from app.services import audit
from app.utils.netease import normalize_netease_playlist_link_field
from app.utils.pagination import PageParams, build_page_meta, page_params

router = APIRouter(prefix="/music", tags=["music"])


def _serialize_list(value) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    return []


def _serialize_story(value) -> dict:
    if not value or not isinstance(value, dict):
        return {}
    return {k: str(v) for k, v in value.items() if k in {"CN", "EN", "JP"} and v is not None and str(v).strip()}


def _to_out(track: MusicTrack) -> MusicTrackOut:
    return MusicTrackOut(
        id=track.id,
        title=track.title,
        artist=track.artist,
        album=track.album,
        genre=track.genre,
        year=track.year,
        duration_seconds=track.duration_seconds,
        cover_url=track.cover_url,
        audio_url=track.audio_url,
        photos=_serialize_list(track.photos),
        story=_serialize_story(track.story),
        tags=_serialize_list(track.tags),
        pinned=bool(track.pinned),
        owner_id=track.owner_id,
        created_at=track.created_at,
        updated_at=track.updated_at,
    )


async def _reload(session: AsyncSession, track_id: int) -> MusicTrack:
    stmt = select(MusicTrack).where(MusicTrack.id == track_id)
    return (await session.execute(stmt)).scalar_one()


@router.get("", response_model=Page[MusicTrackOut], dependencies=[Depends(require_permissions(Perm.MUSIC_READ))])
async def list_music(
    keyword: Optional[str] = Query(None, max_length=200),
    genre: Optional[str] = Query(None, max_length=80),
    year: Optional[int] = Query(None),
    pinned: Optional[bool] = Query(None),
    pp: PageParams = Depends(page_params),
    session: AsyncSession = Depends(get_session),
) -> Page[MusicTrackOut]:
    stmt = select(MusicTrack)
    count_stmt = select(func.count()).select_from(MusicTrack)

    if keyword:
        like = f"%{keyword}%"
        cond = or_(
            MusicTrack.title.ilike(like),
            MusicTrack.artist.ilike(like),
            MusicTrack.album.ilike(like),
            MusicTrack.genre.ilike(like),
            cast(MusicTrack.tags, String).ilike(like),
        )
        stmt = stmt.where(cond)
        count_stmt = count_stmt.where(cond)

    if genre:
        stmt = stmt.where(MusicTrack.genre == genre)
        count_stmt = count_stmt.where(MusicTrack.genre == genre)
    if year is not None:
        stmt = stmt.where(MusicTrack.year == year)
        count_stmt = count_stmt.where(MusicTrack.year == year)
    if pinned is not None:
        stmt = stmt.where(MusicTrack.pinned.is_(pinned))
        count_stmt = count_stmt.where(MusicTrack.pinned.is_(pinned))

    stmt = stmt.order_by(MusicTrack.pinned.desc(), MusicTrack.updated_at.desc(), MusicTrack.id.desc())
    stmt = stmt.offset(pp.offset).limit(pp.page_size)
    rows = (await session.execute(stmt)).scalars().all()
    total = (await session.execute(count_stmt)).scalar_one()
    return Page[MusicTrackOut](items=[_to_out(row) for row in rows], meta=build_page_meta(pp, total))


@router.get("/count", response_model=MusicTrackCount, dependencies=[Depends(require_permissions(Perm.MUSIC_READ))])
async def count_music(session: AsyncSession = Depends(get_session)) -> MusicTrackCount:
    total = (await session.execute(select(func.count()).select_from(MusicTrack))).scalar_one()
    return MusicTrackCount(total=int(total))


@router.get("/{track_id}", response_model=MusicTrackOut, dependencies=[Depends(require_permissions(Perm.MUSIC_READ))])
async def get_music(track_id: int, session: AsyncSession = Depends(get_session)) -> MusicTrackOut:
    track = await session.get(MusicTrack, track_id)
    if not track:
        raise NotFound("音乐不存在")
    return _to_out(track)


@router.post("", response_model=MusicTrackOut, dependencies=[Depends(require_permissions(Perm.MUSIC_WRITE))])
async def create_music(
    request: Request,
    body: MusicTrackCreate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
) -> MusicTrackOut:
    track = MusicTrack(
        title=body.title.strip(),
        artist=body.artist or None,
        album=normalize_netease_playlist_link_field(body.album),
        genre=body.genre or None,
        year=body.year,
        duration_seconds=body.duration_seconds,
        cover_url=body.cover_url or None,
        audio_url=normalize_netease_playlist_link_field(body.audio_url),
        photos=list(body.photos or []),
        story=dict(body.story or {}),
        tags=list(body.tags or []),
        pinned=bool(body.pinned),
        owner_id=user.id,
    )
    session.add(track)
    await session.flush()
    await audit.record(
        session,
        actor=user,
        action=AuditAction.create,
        target_type="music",
        target_id=track.id,
        summary=f"新建音乐 {track.title}",
        request=request,
    )
    track = await _reload(session, track.id)
    return _to_out(track)


@router.patch("/{track_id}", response_model=MusicTrackOut, dependencies=[Depends(require_permissions(Perm.MUSIC_WRITE))])
async def update_music(
    track_id: int,
    request: Request,
    body: MusicTrackUpdate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
) -> MusicTrackOut:
    track = await session.get(MusicTrack, track_id)
    if not track:
        raise NotFound("音乐不存在")
    payload = body.model_dump(exclude_unset=True)

    if "title" in payload and payload["title"] is not None:
        track.title = payload["title"].strip()
    if "artist" in payload:
        track.artist = payload["artist"] or None
    if "album" in payload:
        track.album = normalize_netease_playlist_link_field(payload["album"]) if payload["album"] else None
    if "genre" in payload:
        track.genre = payload["genre"] or None
    if "year" in payload:
        track.year = payload["year"]
    if "duration_seconds" in payload:
        track.duration_seconds = payload["duration_seconds"]
    if "cover_url" in payload:
        track.cover_url = payload["cover_url"] or None
    if "audio_url" in payload:
        track.audio_url = normalize_netease_playlist_link_field(payload["audio_url"]) if payload["audio_url"] else None
    if "photos" in payload and payload["photos"] is not None:
        track.photos = list(payload["photos"])
    if "story" in payload and payload["story"] is not None:
        track.story = dict(payload["story"])
    if "tags" in payload and payload["tags"] is not None:
        track.tags = list(payload["tags"])
    if "pinned" in payload and payload["pinned"] is not None:
        track.pinned = bool(payload["pinned"])

    await session.flush()
    await audit.record(
        session,
        actor=user,
        action=AuditAction.update,
        target_type="music",
        target_id=track.id,
        summary=f"更新音乐 {track.title}",
        request=request,
    )
    track = await _reload(session, track.id)
    return _to_out(track)


@router.post("/{track_id}/pin", response_model=MusicTrackOut, dependencies=[Depends(require_permissions(Perm.MUSIC_WRITE))])
async def toggle_pin(
    track_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
) -> MusicTrackOut:
    track = await session.get(MusicTrack, track_id)
    if not track:
        raise NotFound("音乐不存在")
    track.pinned = not bool(track.pinned)
    await session.flush()
    await audit.record(
        session,
        actor=user,
        action=AuditAction.update,
        target_type="music",
        target_id=track.id,
        summary=("置顶" if track.pinned else "取消置顶") + f" 音乐 {track.title}",
        request=request,
    )
    track = await _reload(session, track.id)
    return _to_out(track)


@router.delete("/{track_id}", response_model=OkResponse, dependencies=[Depends(require_permissions(Perm.MUSIC_DELETE))])
async def delete_music(
    track_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
) -> OkResponse:
    track = await session.get(MusicTrack, track_id)
    if not track:
        raise NotFound("音乐不存在")
    title = track.title
    await session.delete(track)
    await audit.record(
        session,
        actor=user,
        action=AuditAction.delete,
        target_type="music",
        target_id=track_id,
        summary=f"删除音乐 {title}",
        request=request,
    )
    return OkResponse(message="deleted")
