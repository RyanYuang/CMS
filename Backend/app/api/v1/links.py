"""链接管理接口。"""


from fastapi import APIRouter, Depends, Request
from sqlalchemy import case, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import current_user, require_permissions
from app.exceptions import BizError, NotFound
from app.models import AuditAction, LinkItem, User
from app.permissions import Perm
from app.schemas import LinkCreate, LinkOut, LinkReorder, LinkUpdate, OkResponse
from app.services import audit


router = APIRouter(prefix="/links", tags=["links"])


@router.get("", response_model=list[LinkOut])
async def list_links(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(current_user),
) -> list[LinkOut]:
    res = await session.execute(select(LinkItem).order_by(LinkItem.sort_order, LinkItem.id))
    return [LinkOut.model_validate(item) for item in res.scalars().all()]


@router.post(
    "",
    response_model=LinkOut,
    dependencies=[Depends(require_permissions(Perm.LINK_WRITE))],
)
async def create_link(
    request: Request,
    body: LinkCreate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
) -> LinkOut:
    item = LinkItem(**body.model_dump())
    session.add(item)
    await session.flush()
    await audit.record(
        session,
        actor=user,
        action=AuditAction.create,
        target_type="link",
        target_id=item.id,
        summary=f"新增链接 {item.title}",
        request=request,
    )
    return LinkOut.model_validate(item)


@router.patch(
    "/{link_id}",
    response_model=LinkOut,
    dependencies=[Depends(require_permissions(Perm.LINK_WRITE))],
)
async def update_link(
    link_id: int,
    request: Request,
    body: LinkUpdate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
) -> LinkOut:
    item = await session.get(LinkItem, link_id)
    if not item:
        raise NotFound("链接不存在")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await session.flush()
    await audit.record(
        session,
        actor=user,
        action=AuditAction.update,
        target_type="link",
        target_id=item.id,
        summary=f"更新链接 {item.title}",
        request=request,
    )
    return LinkOut.model_validate(item)


@router.post(
    "/reorder",
    response_model=list[LinkOut],
    dependencies=[Depends(require_permissions(Perm.LINK_WRITE))],
)
async def reorder_links(
    body: LinkReorder,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(current_user),
) -> list[LinkOut]:
    if not body.ordered_ids:
        raise BizError("ordered_ids 不能为空")

    res = await session.execute(select(LinkItem).where(LinkItem.id.in_(body.ordered_ids)))
    items = {item.id: item for item in res.scalars().all()}
    if len(items) != len(body.ordered_ids):
        raise BizError("存在未知 link_id")

    for index, link_id in enumerate(body.ordered_ids, start=1):
        items[link_id].sort_order = index

    await session.flush()
    res2 = await session.execute(
        select(LinkItem).order_by(case(
            *[(LinkItem.id == lid, idx) for idx, lid in enumerate(body.ordered_ids)],
            else_=len(body.ordered_ids),
        ))
    )
    return [LinkOut.model_validate(item) for item in res2.scalars().all()]


@router.delete(
    "/{link_id}",
    response_model=OkResponse,
    dependencies=[Depends(require_permissions(Perm.LINK_WRITE))],
)
async def delete_link(
    link_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
) -> OkResponse:
    item = await session.get(LinkItem, link_id)
    if not item:
        raise NotFound("链接不存在")
    title = item.title
    await session.delete(item)
    await audit.record(
        session,
        actor=user,
        action=AuditAction.delete,
        target_type="link",
        target_id=link_id,
        summary=f"删除链接 {title}",
        request=request,
    )
    return OkResponse(message="deleted")
