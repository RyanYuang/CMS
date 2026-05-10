"""站点设置接口。"""


from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import current_user, require_permissions
from app.models import SiteSetting
from app.permissions import Perm
from app.schemas import OkResponse, SettingItem


router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=list[SettingItem])
async def list_settings(
    session: AsyncSession = Depends(get_session),
    _: object = Depends(current_user),
) -> list[SettingItem]:
    res = await session.execute(select(SiteSetting))
    return [SettingItem(key=s.key, value=s.value) for s in res.scalars().all()]


@router.put(
    "",
    response_model=OkResponse,
    dependencies=[Depends(require_permissions(Perm.SETTING_WRITE))],
)
async def upsert_settings(
    items: list[SettingItem],
    session: AsyncSession = Depends(get_session),
) -> OkResponse:
    res = await session.execute(select(SiteSetting))
    existing: dict[str, SiteSetting] = {s.key: s for s in res.scalars().all()}
    for item in items:
        target = existing.get(item.key)
        if target:
            target.value = _clean_value(item.value)
        else:
            session.add(SiteSetting(key=item.key, value=_clean_value(item.value)))
    await session.flush()
    return OkResponse(message="saved")


def _clean_value(value: Any) -> Any:
    if isinstance(value, (dict, list, str, int, float, bool)) or value is None:
        return value
    return str(value)
