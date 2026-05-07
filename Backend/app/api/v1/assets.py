"""资源（媒体）接口（RYA-12/15）。"""

from fastapi import APIRouter, Depends, File, Query, Request, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_session
from app.deps import current_user, require_permissions
from app.exceptions import BizError
from app.models import Asset, AssetKind, AuditAction, User
from app.permissions import Perm
from app.rate_limit import limiter
from app.schemas import AssetListItem, AssetOut, OkResponse
from app.schemas.common import Page, PageMeta
from app.services import asset as asset_service
from app.services import audit
from app.utils.pagination import PageParams, build_page_meta, page_params


router = APIRouter(prefix="/assets", tags=["assets"])


@router.get(
    "",
    response_model=Page[AssetListItem],
    dependencies=[Depends(require_permissions(Perm.ASSET_READ))],
)
async def list_assets(
    kind: AssetKind | None = Query(None),
    is_orphan: bool | None = Query(None),
    keyword: str | None = Query(None, max_length=120),
    pp: PageParams = Depends(page_params),
    session: AsyncSession = Depends(get_session),
) -> Page[AssetListItem]:
    stmt = select(Asset)
    cnt = select(func.count(Asset.id))
    conds = []
    if kind is not None:
        conds.append(Asset.kind == kind)
    if is_orphan is not None:
        conds.append(Asset.is_orphan.is_(is_orphan))
    if keyword:
        like = f"%{keyword}%"
        conds.append(Asset.filename.ilike(like))
    for c in conds:
        stmt = stmt.where(c)
        cnt = cnt.where(c)

    total = (await session.execute(cnt)).scalar_one()
    rows = (
        await session.execute(stmt.order_by(Asset.id.desc()).offset(pp.offset).limit(pp.page_size))
    ).scalars().all()

    return Page[AssetListItem](
        items=[AssetListItem.model_validate(a) for a in rows],
        meta=build_page_meta(pp, int(total)),
    )


@router.post(
    "/upload",
    response_model=AssetOut,
    dependencies=[Depends(require_permissions(Perm.ASSET_WRITE))],
)
@limiter.limit(settings.rate_limit_upload)
async def upload_asset(
    request: Request,
    file: UploadFile = File(...),
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> AssetOut:
    if not file.filename:
        raise BizError("缺少文件名")
    asset = await asset_service.save_file(
        session,
        file=file.file,
        filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        uploader=user,
    )
    await audit.record(
        session,
        actor=user,
        action=AuditAction.upload,
        target_type="asset",
        target_id=asset.id,
        summary=f"上传 {asset.filename}",
        request=request,
    )
    return AssetOut.model_validate(asset)


@router.delete(
    "/{asset_id}",
    response_model=OkResponse,
    dependencies=[Depends(require_permissions(Perm.ASSET_DELETE))],
)
async def delete_asset(
    asset_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_user),
) -> OkResponse:
    await asset_service.remove_asset(session, asset_id)
    await audit.record(
        session,
        actor=user,
        action=AuditAction.delete,
        target_type="asset",
        target_id=asset_id,
        summary=f"删除资源 #{asset_id}",
        request=request,
    )
    return OkResponse(message="deleted")


@router.post(
    "/cleanup-orphans",
    dependencies=[Depends(require_permissions(Perm.ASSET_DELETE))],
)
async def cleanup_orphans(
    dry_run: bool = Query(False),
    session: AsyncSession = Depends(get_session),
) -> dict[str, int]:
    return await asset_service.cleanup_orphans(session, dry_run=dry_run)
