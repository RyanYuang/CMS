"""标签接口。"""


from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import current_user, require_permissions
from app.exceptions import Conflict, NotFound
from app.models import Tag
from app.permissions import Perm
from app.schemas import OkResponse, TagCreate, TagOut
from app.utils.slug import make_slug


router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagOut])
async def list_tags(
    session: AsyncSession = Depends(get_session),
    _: object = Depends(current_user),
) -> list[TagOut]:
    res = await session.execute(select(Tag).order_by(Tag.id))
    return [TagOut.model_validate(t) for t in res.scalars().all()]


@router.post(
    "",
    response_model=TagOut,
    dependencies=[Depends(require_permissions(Perm.TAG_WRITE))],
)
async def create_tag(
    body: TagCreate,
    session: AsyncSession = Depends(get_session),
) -> TagOut:
    slug = body.slug or make_slug(body.name)
    exists = (await session.execute(select(Tag).where(Tag.slug == slug))).scalar_one_or_none()
    if exists:
        raise Conflict("slug 已存在")
    tag = Tag(name=body.name, slug=slug)
    session.add(tag)
    await session.flush()
    return TagOut.model_validate(tag)


@router.delete(
    "/{tag_id}",
    response_model=OkResponse,
    dependencies=[Depends(require_permissions(Perm.TAG_WRITE))],
)
async def delete_tag(
    tag_id: int,
    session: AsyncSession = Depends(get_session),
) -> OkResponse:
    tag = await session.get(Tag, tag_id)
    if not tag:
        raise NotFound("标签不存在")
    await session.delete(tag)
    return OkResponse(message="deleted")
