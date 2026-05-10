"""笔记接口：list/get/create/update/delete/togglePin/count。"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import current_user, require_permissions
from app.exceptions import NotFound
from app.models import AuditAction, Note, User
from app.permissions import Perm
from app.schemas import NoteCount, NoteCreate, NoteOut, NoteUpdate, OkResponse
from app.schemas.common import Page
from app.services import audit
from app.utils.pagination import PageParams, build_page_meta, page_params


router = APIRouter(prefix="/notes", tags=["notes"])


def _serialize_tags(value) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(t) for t in value if t is not None]
    return []


def _to_out(note: Note) -> NoteOut:
    return NoteOut(
        id=note.id,
        title=note.title,
        content=note.content or "",
        category=note.category,
        pinned=bool(note.pinned),
        tags=_serialize_tags(note.tags),
        owner_id=note.owner_id,
        created_at=note.created_at,
        updated_at=note.updated_at,
    )


async def _reload(session: AsyncSession, note_id: int) -> Note:
    """重新查询笔记，避免 onupdate 触发后 updated_at 在异步上下文中懒加载失败。"""
    stmt = select(Note).where(Note.id == note_id)
    return (await session.execute(stmt)).scalar_one()


@router.get(
    "",
    response_model=Page[NoteOut],
    dependencies=[Depends(require_permissions(Perm.NOTE_READ))],
)
async def list_notes(
    keyword: Optional[str] = Query(None, max_length=200),
    category: Optional[str] = Query(None, max_length=80),
    pp: PageParams = Depends(page_params),
    session: AsyncSession = Depends(get_session),
) -> Page[NoteOut]:
    stmt = select(Note)
    count_stmt = select(func.count()).select_from(Note)

    if keyword:
        like = f"%{keyword}%"
        cond = or_(
            Note.title.ilike(like),
            Note.content.ilike(like),
            cast(Note.tags, String).ilike(like),
        )
        stmt = stmt.where(cond)
        count_stmt = count_stmt.where(cond)

    if category:
        stmt = stmt.where(Note.category == category)
        count_stmt = count_stmt.where(Note.category == category)

    stmt = stmt.order_by(Note.pinned.desc(), Note.updated_at.desc(), Note.id.desc())
    stmt = stmt.offset(pp.offset).limit(pp.page_size)

    rows = (await session.execute(stmt)).scalars().all()
    total = (await session.execute(count_stmt)).scalar_one()

    return Page[NoteOut](
        items=[_to_out(n) for n in rows],
        meta=build_page_meta(pp, total),
    )


@router.get(
    "/count",
    response_model=NoteCount,
    dependencies=[Depends(require_permissions(Perm.NOTE_READ))],
)
async def count_notes(session: AsyncSession = Depends(get_session)) -> NoteCount:
    total = (await session.execute(select(func.count()).select_from(Note))).scalar_one()
    return NoteCount(total=int(total))


@router.get(
    "/{note_id}",
    response_model=NoteOut,
    dependencies=[Depends(require_permissions(Perm.NOTE_READ))],
)
async def get_note(
    note_id: int,
    session: AsyncSession = Depends(get_session),
) -> NoteOut:
    note = await session.get(Note, note_id)
    if not note:
        raise NotFound("笔记不存在")
    return _to_out(note)


@router.post(
    "",
    response_model=NoteOut,
    dependencies=[Depends(require_permissions(Perm.NOTE_WRITE))],
)
async def create_note(
    request: Request,
    body: NoteCreate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
) -> NoteOut:
    note = Note(
        title=body.title.strip(),
        content=body.content or "",
        category=(body.category or None),
        pinned=bool(body.pinned),
        tags=list(body.tags or []),
        owner_id=user.id,
    )
    session.add(note)
    await session.flush()
    await audit.record(
        session,
        actor=user,
        action=AuditAction.create,
        target_type="note",
        target_id=note.id,
        summary=f"新建笔记 {note.title}",
        request=request,
    )
    note = await _reload(session, note.id)
    return _to_out(note)


@router.patch(
    "/{note_id}",
    response_model=NoteOut,
    dependencies=[Depends(require_permissions(Perm.NOTE_WRITE))],
)
async def update_note(
    note_id: int,
    request: Request,
    body: NoteUpdate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
) -> NoteOut:
    note = await session.get(Note, note_id)
    if not note:
        raise NotFound("笔记不存在")

    payload = body.model_dump(exclude_unset=True)
    if "title" in payload and payload["title"] is not None:
        note.title = payload["title"].strip()
    if "content" in payload and payload["content"] is not None:
        note.content = payload["content"]
    if "category" in payload:
        note.category = payload["category"] or None
    if "pinned" in payload and payload["pinned"] is not None:
        note.pinned = bool(payload["pinned"])
    if "tags" in payload and payload["tags"] is not None:
        note.tags = list(payload["tags"])

    await session.flush()
    await audit.record(
        session,
        actor=user,
        action=AuditAction.update,
        target_type="note",
        target_id=note.id,
        summary=f"更新笔记 {note.title}",
        request=request,
    )
    note = await _reload(session, note.id)
    return _to_out(note)


@router.post(
    "/{note_id}/pin",
    response_model=NoteOut,
    dependencies=[Depends(require_permissions(Perm.NOTE_WRITE))],
)
async def toggle_pin(
    note_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
) -> NoteOut:
    note = await session.get(Note, note_id)
    if not note:
        raise NotFound("笔记不存在")
    note.pinned = not bool(note.pinned)
    await session.flush()
    await audit.record(
        session,
        actor=user,
        action=AuditAction.update,
        target_type="note",
        target_id=note.id,
        summary=("置顶" if note.pinned else "取消置顶") + f" 笔记 {note.title}",
        request=request,
    )
    note = await _reload(session, note.id)
    return _to_out(note)


@router.delete(
    "/{note_id}",
    response_model=OkResponse,
    dependencies=[Depends(require_permissions(Perm.NOTE_DELETE))],
)
async def delete_note(
    note_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
) -> OkResponse:
    note = await session.get(Note, note_id)
    if not note:
        raise NotFound("笔记不存在")
    title = note.title
    await session.delete(note)
    await audit.record(
        session,
        actor=user,
        action=AuditAction.delete,
        target_type="note",
        target_id=note_id,
        summary=f"删除笔记 {title}",
        request=request,
    )
    return OkResponse(message="deleted")
