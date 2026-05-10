"""审计日志服务（RYA-11）。"""

from __future__ import annotations

from typing import Dict, Optional, Union, Any

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditAction, AuditLog, User


def _request_ip(request: Optional[Request]) -> Optional[str]:
    if not request:
        return None
    if request.client and request.client.host:
        return request.client.host
    return request.headers.get("x-forwarded-for") or request.headers.get("x-real-ip")


async def record(
    session: AsyncSession,
    *,
    actor: Optional[User],
    action: AuditAction,
    target_type: str,
    target_id: Optional[Union[str, int]] = None,
    summary: Optional[str] = None,
    diff: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None,
) -> AuditLog:
    log = AuditLog(
        actor_id=actor.id if actor else None,
        actor_username=actor.username if actor else None,
        action=action,
        target_type=target_type,
        target_id=str(target_id) if target_id is not None else None,
        summary=summary,
        diff=diff,
        request_ip=_request_ip(request),
    )
    session.add(log)
    await session.flush()
    return log
