"""审计日志查询接口。"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import require_permissions
from app.models import AuditAction, AuditLog
from app.permissions import Perm
from app.schemas import AuditLogOut
from app.schemas.common import Page
from app.utils.pagination import PageParams, build_page_meta, page_params


router = APIRouter(prefix="/audit", tags=["audit"])


@router.get(
    "",
    response_model=Page[AuditLogOut],
    dependencies=[Depends(require_permissions(Perm.AUDIT_READ))],
)
async def list_audit(
    target_type: Optional[str] = Query(None, max_length=64),
    target_id: Optional[str] = Query(None, max_length=64),
    actor_id: Optional[int] = Query(None),
    action: Optional[AuditAction] = Query(None),
    pp: PageParams = Depends(page_params),
    session: AsyncSession = Depends(get_session),
) -> Page[AuditLogOut]:
    stmt = select(AuditLog)
    cnt = select(func.count(AuditLog.id))
    conds = []
    if target_type:
        conds.append(AuditLog.target_type == target_type)
    if target_id:
        conds.append(AuditLog.target_id == target_id)
    if actor_id:
        conds.append(AuditLog.actor_id == actor_id)
    if action:
        conds.append(AuditLog.action == action)
    for c in conds:
        stmt = stmt.where(c)
        cnt = cnt.where(c)

    total = (await session.execute(cnt)).scalar_one()
    rows = (
        await session.execute(stmt.order_by(AuditLog.id.desc()).offset(pp.offset).limit(pp.page_size))
    ).scalars().all()
    return Page[AuditLogOut](
        items=[AuditLogOut.model_validate(r) for r in rows],
        meta=build_page_meta(pp, int(total)),
    )
